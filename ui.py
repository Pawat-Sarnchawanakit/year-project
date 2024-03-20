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
    # figure: Figure
    db: Database

    def __init__(self) -> None:
        super().__init__()
        self.load_all_dataset()
        self.title("Project")
        self.init_components()

    def load_all_dataset(self):
        db = Database()
        for file in Path("./dataset/").iterdir():
            if not file.is_file():
                continue
            db.add_source(file)
        self.db = db

    def init_components(self):
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
        compiled_data = CompiledData(self.db.sources, (lambda val: True,), lambda ins: ins.name)
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
        canvas = SimpleChartWidget(self, compiled_data)  # Convert the Figure to a tkinter widget
        canvas.get_tk_widget().grid(sticky=tk.NSEW)
        # canvas.draw()
        self.canvas = canvas
        chart_type_combobox = customtkinter.CTkComboBox(self, values=("Histogram", "Pie Chart"), command=self.on_chart_type_selected)
        # plt = self.figure.add_subplot(111)
        # layout = nwx.kamada_kawai_layout(graph, scale=2)
        # nwx.draw_networkx_nodes(graph, layout, node_color='steelblue', node_size=300, ax=plt)
        # nwx.draw_networkx_edges(graph, layout, edge_color='gray', ax=plt)
        self.on_chart_type_selected("Histogram")
        chart_type_combobox.grid(row=1, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def on_chart_type_selected(self, choice):
        if choice == "Histogram":
            return self.canvas.render(ChartType.HISTOGRAM)
        if choice == "Pie Chart":
            return self.canvas.render(ChartType.PIE_CHART)
        # fig = self.figure
        # fig.clear()
        # plt = fig.add_subplot(111)
        # if choice == "Histogram":
        #     ticks = range(len(self.frequency_data[0]))
        #     plt.barh(ticks, self.frequency_data[1])
        #     plt.set_yticks(ticks, self.frequency_data[0])
        # elif choice == "Pie":
        #     plt.pie(self.frequency_data[1], labels=self.frequency_data[0])
        # self.canvas.draw()

    def show(self):
        self.mainloop()
