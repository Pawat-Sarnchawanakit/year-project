import tkinter as tk
import networkx as nwx
from pathlib import Path
from itertools import chain
from collections import Counter
from chart import SimpleChartWidget, ChartType
from matplotlib.figure import Figure
import customtkinter
from data import Database, CompiledData


class MainForm(customtkinter.CTk):
    """The main form of the application."""
    db: Database
    chart_widget: SimpleChartWidget

    def __init__(self) -> None:
        super().__init__()
        self.load_all_dataset()
        self.title("Project")
        self.init_components()

    def load_all_dataset(self) -> None:
        """Loads all data sets into memory."""
        db = Database()
        for file in Path("./dataset/").iterdir():
            if not file.is_file():
                continue
            db.add_source(file)
        self.db = db

    def init_components(self) -> None:
        """Initialize each componenents."""
        # self.figure = Figure(figsize=(6, 6))
        # graph = nwx.DiGraph()
        # graph.add_nodes_from(set(map(lambda val: val.class_name, chain(*map(lambda source: source.everything(), self.db.sources)))))
        # stack = [(source.root, None) for source in self.db.sources]
        # dup = set()
        # while stack:
        #     cur = stack.pop()
        #     if cur[1] is not None:
        #         dup_check = frozenset((cur[1], cur[0].class_name))
        #         if dup_check not in dup:
        #             dup.add(dup_check)
        #             # print(cur[1], cur[0].class_name)
        #             graph.add_edge(cur[1], cur[0].class_name)
        #     if cur[0].children:
        #         for child in cur[0].children:
        #             stack.append((child, cur[0].class_name))
        # bucket = Counter(map(lambda val: val.class_name, filter(lambda val: not any(map(lambda ancestor: ancestor.class_name == "Model", val.ancestors())), chain(*map(lambda source: source.everything(), db.sources)))))
        # bucket = Counter(map(lambda val: val.class_name, filter(lambda val: sum(1 for _ in val.ancestors()) == 10, chain(*map(lambda source: source.everything(), db.sources)))))
        compiled_data = CompiledData(self.db.sources, (lambda val: True,), lambda ins: len(ins.name))
        print("Mean name length", compiled_data.mean)
        print("Median name length", compiled_data.median)
        print("Name length SD", compiled_data.stdev)
        # counter = Counter(map(lambda val: val.class_name, chain(*self.db)))
        # bucket = list(counter.most_common())
        # bucket.append(("Other", counter.total()-sum(v[1] for v in bucket)))
        # bucket.sort(key=lambda v: v[1], reverse=True)
        # self.frequency_data = ([val[0] for val in bucket], [val[1] for val in bucket])
        # # bucket = Counter(map(lambda val: val.depth(), chain(*db))).items()
        # print(bucket)
        # plt = fig.add_subplot(111)
        # plt = self.figure.add_subplot(111)
        # layout = nwx.kamada_kawai_layout(graph, scale=2)
        # nwx.draw_networkx_nodes(graph, layout, node_color='steelblue', node_size=300, ax=plt)
        # nwx.draw_networkx_edges(graph, layout, edge_color='gray', ax=plt)
        chart_widget = SimpleChartWidget(self, compiled_data)  # Convert the Figure to a tkinter widget
        chart_widget.get_tk_widget().grid(sticky=tk.NSEW)
        chart_widget.options.chart_type = ChartType.HISTOGRAM
        self.chart_widget = chart_widget
        chart_type_combobox = customtkinter.CTkComboBox(self, values=ChartType.strings(), command=self.on_chart_type_selected, state="readonly") 
        chart_type_combobox.grid(row=1, column=0, sticky=tk.NSEW)
        render_button = customtkinter.CTkButton(self, text="Render", command=chart_widget.render)
        render_button.grid(row=1, column=1, sticky=tk.NSEW)
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(0, weight=1)

    def on_chart_type_selected(self, choice) -> None:
        """Fired when the chart type combobox is selected."""
        self.chart_widget.options.chart_type = ChartType.string_to_enum_map()[choice]

    def show(self) -> None:
        self.mainloop()

# class ChartTab(customtkinter.CTkFrame):
#     chart_type_combobox: customtkinter.CTkComboBox

#     def __init__(self, parent, **kwargs):
#         super().__init__(parent, **kwargs)

#     def init_components(self):
#         chart_type_label = customtkinter.CTkLabel(self, text="Chart Type")
#         self.chart_type_combobox = customtkinter.CTkComboBox(self, values=ChartType.strings()) 
#         self.chart_type_combobox.grid(row=0, column=0, sticky=tk.NSEW)