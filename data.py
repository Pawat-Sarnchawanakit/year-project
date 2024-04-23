"""This file implements data loading, compiling, and transformation."""
from typing import List, Tuple, Any, TypedDict, Self, cast, Generator, Iterable, Callable
from pathlib import Path
from itertools import chain
from collections import Counter
from json import load as load_json
from dataclasses import dataclass
from statistics import quantiles, mean, stdev

RawInstance = TypedDict("RawInstance", {
    "name": str | None,
    "class": str | None,
    "children": Any | None
})


@dataclass
class Instance:
    """An `instance` in Roblox terms or an `object`."""
    name: str
    class_name: str
    parent: Self | None
    children: List[Self] | None

    def depth(self) -> int:
        """Returns the depth of the instance.

        Returns:
            int: The depth of the instance.
        """
        depth = 0
        parent: Self | None = self.parent
        while parent is not None:
            depth += 1
            parent = parent.parent
        return depth

    def ancestors(self) -> Generator[Self, None, None]:
        """Returns a generator that goes through the instance parents iteratively.

        Yields:
            Generator[Self, None, None]: The generator.
        """
        parent: Self | None = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent

    def descendants(self) -> Generator[Self, None, None]:
        """Returns a generator that goes through the instance's descendants.

        Yields:
            Generator[Self, None, None]: The generator.
        """
        if not self.children:
            return
        stack: List[List[Self]] = []
        stack.append(self.children)
        while stack:
            top = stack.pop()
            for child in top:
                yield child
                if child.children:
                    stack.append(child.children)

    def everything(self) -> Generator[Self, None, None]:
        """Returns a generator that goes through the instance recursively.

        Yields:
            Generator[Self, None, None]: The generator.
        """
        yield self
        yield from self.descendants()


@dataclass
class DataSource:
    """Stores the entire parsed tree, and the origin of the tree.
    """
    source_path: Path
    root: Instance

    def everything(self) -> Generator[Instance, None, None]:
        """Calls root.everything()"""
        yield from self

    def __iter__(self) -> Generator[Instance, None, None]:
        yield from self.root.everything()


class Database:
    """Stores a list of data sources and precomputed data."""
    __sources: List[DataSource]

    def __init__(self) -> None:
        self.__sources = []

    @property
    def sources(self) -> List[DataSource]:
        """The sources."""
        return self.__sources

    def add_source(self, path: Path) -> None:
        """Add a source.

        Args:
            path (Path): The path of the source.

        Raises:
            ValueError: Path doesn't exist.
            ValueError: Failed to load source.
        """
        if not path.exists():
            raise ValueError("Path doesn't exist.")
        data: RawInstance | None = None
        with open(path, encoding="UTF-8") as file:
            data = load_json(file)
        if data is None:
            raise ValueError("Failed to load source.")
        root: Instance | None = None
        stack: List[Tuple[RawInstance, Instance | None]] = [(data, None)]
        while stack:
            raw, parent = stack.pop()
            children = cast(List[RawInstance], raw.get("children"))
            new_child = Instance(name=raw.get("name") or "",
                                 class_name=raw.get("class") or "",
                                 parent=parent,
                                 children=[] if children else None)
            if parent is None:
                root = new_child
            else:
                cast(List[Instance], parent.children).append(new_child)
            if children is None:
                continue
            for child in children:
                stack.append((child, new_child))
        self.__sources.append(DataSource(path, cast(Instance, root)))

    def __iter__(self) -> Generator[DataSource, None, None]:
        yield from self.__sources


@dataclass
class Range:
    """A range with a low value and high value"""
    low: float | int
    high: float | int


class CompiledData:
    """A compiled data.
    """
    range: Range
    first_quadrant: float | int
    median: float | int
    third_quadrant: float | int
    stdev: float | int
    mean: float | int
    frequency: Counter
    num_data: List[int | float]

    def __init__(self):
        self.range = 0
        self.first_quadrant = 0
        self.median = 0
        self.third_quadrant = 0
        self.stdev = 0
        self.mean = 0
        self.frequency = Counter()
        self.num_data = []

    def compile(self, data_sources: Iterable[DataSource],
                 key: Callable[[Instance], Any],
                 test: Callable[[Instance], bool]) -> None:
        """Compiles the data."""
        data: List[Any] = list(
            map(
                key,
                filter(
                    test,
                    chain(*map(lambda source: source.everything(),
                               data_sources)))))
        self.frequency = Counter(data)
        if not data:
            return
        if not isinstance(data[0], int | float):
            data = cast(List[Any], self.frequency.values())
        self.num_data = data
        self.mean = mean(data)
        self.stdev = stdev(data)
        self.range = Range(low=min(data), high=max(data))
        if len(data) > 2:
            quatiles: List[float] = quantiles(data)
            # pylint: disable=unbalanced-tuple-unpacking
            self.first_quadrant, self.median, self.third_quadrant = quatiles
