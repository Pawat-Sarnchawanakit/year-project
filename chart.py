from enum import Enum, auto
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from data import CompiledData


class ChartType(Enum):
    """Different types of charts."""
    HISTOGRAM = auto()
    PIE_CHART = auto()


class SimpleChartWidget(FigureCanvasTkAgg):
    """A simple chart widget."""
    figure: Figure
    compiled_data: CompiledData

    def __init__(self, parent, compiled_data: CompiledData):
        figure = Figure((6, 6))
        super().__init__(figure, master=parent)
        self.figure = figure
        self.compiled_data = compiled_data

    def render(self, chart_type: ChartType) -> None:
        """Renders the chart."""
        fig = self.figure
        fig.clear()
        plt = fig.add_subplot(111)
        self.render_internal(plt, chart_type)
        self.draw()

    def render_internal(self, plt: Axes, chart_type: ChartType) -> None:
        """Internal method used to render the chart."""
        counter = self.compiled_data.frequency
        bucket = list(counter.most_common(32))
        bucket.append(("Other", counter.total() - sum(v[1] for v in bucket)))
        bucket.sort(key=lambda v: v[1], reverse=True)
        frequency_data = ([val[0]
                           for val in bucket], [val[1] for val in bucket])
        if chart_type == ChartType.HISTOGRAM:
            ticks = range(len(frequency_data[0]))
            plt.barh(ticks, frequency_data[1])
            plt.set_yticks(ticks, frequency_data[0])
            return
        if chart_type == ChartType.PIE_CHART:
            plt.pie(frequency_data[1], labels=frequency_data[0])
            return
