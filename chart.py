from enum import Enum, auto, member
from dataclasses import dataclass
from typing import Tuple, List, Self, Dict, Any
from functools import cache
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from data import CompiledData

class StringEnum(Enum):
    """Extends Enum."""
    @classmethod
    @cache
    def strings(cls) -> Tuple[str, ...]:
        """Return the strings of each enum,
        replacing '_' with a space and converted to title case.

        Returns:
            Tuple[str, ...]: The strings.
        """
        strings: List[str] = []
        for enum in cls:
            strings.append(enum.name.replace("_", " ").title())
        return tuple(strings)

    @classmethod
    @cache
    def string_to_enum_map(cls) -> Dict[str, Any]:
        """Returns a map that maps a string to an enum.

        Returns:
            Dict[str, Self]: The map.
        """
        dict_map: Dict[str, Any] = {}
        for enum in cls:
            dict_map[enum.name.replace("_", " ").title()] = enum
        return dict_map

class ChartKey(StringEnum):
    """Different types of chart keys."""
    NAME = member(lambda val: val.name)
    CLASSNAME = member(lambda val: val.class_name)
    NAME_LENGTH = member(lambda val: len(val.name))
    CLASSNAME_LENGTH = member(lambda val: len(val.class_name))
    NUMBER_OF_CHILDREN = member(lambda val: len(val.children) if val.children is not None else 0)
    DEPTH = member(lambda val: sum(1 for _ in val.ancestors()))


class ChartType(StringEnum):
    """Different types of charts."""
    HISTOGRAM = auto()
    PIE_CHART = auto()
    BOX_PLOT = auto()

@dataclass
class SimpleChartWidgetOptions:
    """The options for the simple chart widget."""
    chart_type: ChartType = ChartType.HISTOGRAM
    show_others: bool = False
    show_common_amount: int = 32
    chart_title: str = ""
    chart_x_axis_title: str = ""
    chart_y_axis_title: str = ""


class SimpleChartWidget(FigureCanvasTkAgg):
    """A simple chart widget."""
    figure: Figure
    compiled_data: CompiledData
    options: SimpleChartWidgetOptions

    def __init__(self, parent, compiled_data: CompiledData):
        figure = Figure((6, 6))
        super().__init__(figure, master=parent)
        self.figure = figure
        self.compiled_data = compiled_data
        self.options = SimpleChartWidgetOptions()

    def render(self) -> None:
        """Renders the chart."""
        fig = self.figure
        fig.clear()
        plt = fig.add_subplot(111)
        self.render_internal(plt)
        self.draw()

    def render_internal(self, plt: Axes) -> None:
        """Internal method used to render the chart."""
        counter = self.compiled_data.frequency
        bucket = list(counter.most_common(self.options.show_common_amount))
        if self.options.show_others:
            bucket.append(("Other", counter.total() - sum(v[1] for v in bucket)))
            bucket.sort(key=lambda v: v[1], reverse=True)
        frequency_data = ([val[0]
                           for val in bucket], [val[1] for val in bucket])
        chart_type = self.options.chart_type
        plt.set_title(self.options.chart_title)
        plt.set_xlabel(self.options.chart_x_axis_title)
        plt.set_ylabel(self.options.chart_y_axis_title)
        if chart_type == ChartType.HISTOGRAM:
            ticks = range(len(frequency_data[0]))
            plt.barh(ticks, frequency_data[1])
            plt.set_yticks(ticks, frequency_data[0])
            return
        if chart_type == ChartType.PIE_CHART:
            plt.pie(frequency_data[1], labels=frequency_data[0])
            return
        if chart_type == ChartType.BOX_PLOT:
            plt.boxplot(self.compiled_data.num_data)
            return
