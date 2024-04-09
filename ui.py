import tkinter as tk
import networkx as nwx
from pathlib import Path
from itertools import chain
from collections import Counter
from chart import SimpleChartWidget, ChartType, ChartKey
from matplotlib.figure import Figure
import customtkinter
from data import Database, CompiledData


class MainForm(customtkinter.CTk):
    """The main form of the application."""
    chart_widget: SimpleChartWidget

    def __init__(self) -> None:
        super().__init__()
        self.title("Project")
        self.init_components()

    def load_all_dataset(self) -> Database:
        """Loads all data sets into memory."""
        db = Database()
        for file in Path("./dataset/").iterdir():
            if not file.is_file():
                continue
            db.add_source(file)
            # break  # Remove when done debugging
        return db

    def init_components(self) -> None:
        """Initialize each componenents."""
        tab_view = customtkinter.CTkTabview(master=self)
        tab_view.pack(expand=True, fill=tk.BOTH)
        for tab_name in ("Chart", "Graph", "Tree"):
            tab_view.add(tab_name)
        tab_view.set("Chart")
        database = self.load_all_dataset()
        chart_tab = ChartTab(tab_view.tab("Chart"), database)
        chart_tab.pack(expand=True, fill=tk.BOTH)
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

        # compiled_data = CompiledData(self.db.sources, (lambda val: True,), lambda ins: len(ins.name))
        # print("Mean name length", compiled_data.mean)
        # print("Median name length", compiled_data.median)
        # print("Name length SD", compiled_data.stdev)

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
        # chart_widget = SimpleChartWidget(self, compiled_data)  # Convert the Figure to a tkinter widget
        # chart_widget.get_tk_widget().grid(sticky=tk.NSEW)
        # chart_widget.options.chart_type = ChartType.HISTOGRAM
        # self.chart_widget = chart_widget
        # chart_type_combobox = customtkinter.CTkComboBox(self, values=ChartType.strings(), command=self.on_chart_type_selected, state="readonly")
        # chart_type_combobox.grid(row=1, column=0, sticky=tk.NSEW)
        # render_button = customtkinter.CTkButton(self, text="Render", command=chart_widget.render)
        # render_button.grid(row=1, column=1, sticky=tk.NSEW)
        # self.rowconfigure(0, weight=100)
        # self.rowconfigure(1, weight=1)
        # self.columnconfigure(0, weight=10)
        # self.columnconfigure(0, weight=1)

    def on_chart_type_selected(self, choice) -> None:
        """Fired when the chart type combobox is selected."""
        self.chart_widget.options.chart_type = ChartType.string_to_enum_map(
        )[choice]

    def show(self) -> None:
        """Show the form."""
        self.mainloop()


class ChartTab(customtkinter.CTkFrame):
    """The chart tab."""
    db: Database
    compiled_data: CompiledData
    chart_widget: SimpleChartWidget
    chart_type_combobox: customtkinter.CTkComboBox
    show_others_checkbox: customtkinter.CTkCheckBox
    highest_count_string: tk.StringVar
    chart_title_string: tk.StringVar
    chart_x_axis_title_string: tk.StringVar
    chart_y_axis_title_string: tk.StringVar
    key_type: ChartKey

    def __init__(self, parent, database, **kwargs):
        self.db = database
        super().__init__(parent, **kwargs)
        self.compiled_data = CompiledData()
        self.init_components()

    # def compile_data(self, key_type: ChartKey):
    #     """Compile the data."""
    #     self.compiled_data = CompiledData(self.db.sources,
    #                                       (lambda val: True, ),
    #                                       key_type.value)

    def on_chart_type_selected(self, choice) -> None:
        """Fired when the chart type combobox is selected."""
        self.chart_widget.options.chart_type = ChartType.string_to_enum_map()[choice]

    def on_highest_count_changed(self, *_):
        """Fired when highest count changed."""
        value = self.highest_count_string.get()
        stripped_value = ""
        for char in value:
            if char.isdigit():
                stripped_value += char
        if stripped_value != value:
            self.highest_count_string.set(stripped_value)
            return
        self.chart_widget.options.show_common_amount = int(
            stripped_value) if stripped_value else 0

    def on_show_others_changed(self):
        """Fired when show others is changed."""
        self.chart_widget.options.show_others = self.show_others_checkbox.get(
        ) == 1

    def on_chart_title_changed(self, *_):
        """Fired when chart title is changed."""
        self.chart_widget.options.chart_title = self.chart_title_string.get()

    def on_chart_x_axis_title_changed(self, *_):
        """Fired when chart title is changed."""
        self.chart_widget.options.chart_x_axis_title = self.chart_x_axis_title_string.get(
        )

    def on_chart_y_axis_title_changed(self, *_):
        """Fired when chart title is changed."""
        self.chart_widget.options.chart_y_axis_title = self.chart_y_axis_title_string.get(
        )

    def on_chart_key_type_selected(self, choice):
        """Fired when chart key type is changed."""
        self.key_type = ChartKey.string_to_enum_map()[choice]
        self.compiled_data.compile(self.db.sources,
                                          (lambda val: True, ),
                                          self.key_type.value)

    def init_components(self):
        """Initialize the widgets."""
        chart_widget = SimpleChartWidget(self, self.compiled_data)
        chart_widget.get_tk_widget().grid(column=0, row=0, sticky="nsew")
        self.chart_widget = chart_widget

        options_frame = customtkinter.CTkFrame(self)

        chart_type_label = customtkinter.CTkLabel(options_frame)
        chart_type_label.configure(takefocus=False, text='Chart Type')
        chart_type_label.grid(column=0, row=0, sticky="nsew")
        chart_type_combobox = customtkinter.CTkComboBox(
            options_frame,
            values=ChartType.strings(),
            command=self.on_chart_type_selected,
            state="readonly")
        chart_type_combobox.set(ChartType.strings()[0])
        chart_widget.options.chart_type = ChartType.HISTOGRAM
        chart_type_combobox.grid(column=1, row=0, sticky="nsew")

        chart_display_type_label = customtkinter.CTkLabel(options_frame)
        chart_display_type_label.configure(takefocus=False, text='Key')
        chart_display_type_label.grid(column=0, row=2, sticky="nsew")
        chart_display_type_combobox = customtkinter.CTkComboBox(
            options_frame,
            values=ChartKey.strings(),
            command=self.on_chart_key_type_selected,
            state="readonly")
        chart_display_type_combobox.set(ChartKey.strings()[0])
        self.on_chart_key_type_selected(chart_display_type_combobox.get())
        chart_display_type_combobox.grid(column=1, row=2, sticky="nsew")

        highest_count_label = customtkinter.CTkLabel(options_frame)
        highest_count_label.configure(text='Highest count')
        highest_count_label.grid(column=0, row=1, sticky="nsew")
        highest_count_string = tk.StringVar(value="32")
        highest_count_string.trace('w', self.on_highest_count_changed)
        self.highest_count_string = highest_count_string
        chart_widget.options.show_common_amount = 32
        highest_count_entry = customtkinter.CTkEntry(
            options_frame, textvariable=highest_count_string)
        highest_count_entry.grid(column=1, row=1, sticky="nsew")

        show_others_checkbox = customtkinter.CTkCheckBox(
            options_frame, command=self.on_show_others_changed)
        show_others_checkbox.configure(text='Show others')
        show_others_checkbox.grid(column=0, row=3, columnspan=2)
        self.show_others_checkbox = show_others_checkbox

        chart_title_label = customtkinter.CTkLabel(options_frame)
        chart_title_label.configure(text='Chart Title')
        chart_title_label.grid(column=2, row=0, sticky="nsew")
        chart_title_string = tk.StringVar(value="Histogram of Instance Name")
        chart_title_string.trace('w', self.on_chart_title_changed)
        self.chart_title_string = chart_title_string
        self.on_chart_title_changed()
        char_title_entry = customtkinter.CTkEntry(
            options_frame, textvariable=chart_title_string)
        char_title_entry.grid(column=3, row=0, sticky="nsew")

        chart_x_axis_label = customtkinter.CTkLabel(options_frame)
        chart_x_axis_label.configure(text='Chart X-Axis Title')
        chart_x_axis_label.grid(column=2, row=1, sticky="nsew")
        chart_x_axis_title_string = tk.StringVar(value="Count")
        chart_x_axis_title_string.trace('w',
                                        self.on_chart_x_axis_title_changed)
        self.chart_x_axis_title_string = chart_x_axis_title_string
        self.on_chart_x_axis_title_changed()
        chart_x_axis_title_entry = customtkinter.CTkEntry(
            options_frame, textvariable=chart_x_axis_title_string)
        chart_x_axis_title_entry.grid(column=3, row=1, sticky="nsew")

        chart_y_axis_label = customtkinter.CTkLabel(options_frame)
        chart_y_axis_label.configure(text='Chart Y-Axis Title')
        chart_y_axis_label.grid(column=2, row=2, sticky="nsew")
        chart_y_axis_title_string = tk.StringVar(value="Name")
        chart_y_axis_title_string.trace('w',
                                        self.on_chart_y_axis_title_changed)
        self.chart_y_axis_title_string = chart_y_axis_title_string
        self.on_chart_y_axis_title_changed()
        chart_y_axis_title_entry = customtkinter.CTkEntry(
            options_frame, textvariable=chart_y_axis_title_string)
        chart_y_axis_title_entry.grid(column=3, row=2, sticky="nsew")

        filter_frame = customtkinter.CTkFrame(options_frame)
        filters_label = customtkinter.CTkLabel(filter_frame)
        filters_label.configure(anchor="center", text='Filters')
        filters_label.grid(column=0, row=0, sticky="new")
        filter_entries_frame = customtkinter.CTkFrame(filter_frame)
        filter_entries_frame.grid(column=0, row=1, sticky="nsew")
        filter_frame.grid(column=0, columnspan=2, row=4, sticky="nsew")
        filter_frame.rowconfigure(0, minsize=20 , weight=100)
        filter_frame.rowconfigure(1, weight=1)
        filter_frame.rowconfigure(1, weight=100, minsize=30)
        filter_frame.rowconfigure("all", weight=100)
        filter_frame.columnconfigure(0, weight=1)
        
        data_sources_frame = customtkinter.CTkFrame(options_frame)
        frame9 = customtkinter.CTkFrame(data_sources_frame)
        frame9.grid(column=0, row=1, sticky="nsew")
        button2 = customtkinter.CTkButton(data_sources_frame)
        button2.configure(text='Recompile data')
        button2.grid(column=0, row=2)
        label9 = customtkinter.CTkLabel(data_sources_frame)
        label9.configure(anchor="center", text='Sources')
        label9.grid(column=0, row=0, sticky="nsew")
        data_sources_frame.grid(column=2, row=4, columnspan=2, sticky="nsew")
        data_sources_frame.rowconfigure(0, weight=10, minsize=20)
        data_sources_frame.rowconfigure(1, weight=1)
        data_sources_frame.rowconfigure(2, weight=10, minsize=30)
        data_sources_frame.rowconfigure("all", weight=1)
        data_sources_frame.columnconfigure(0, weight=1)
        data_sources_frame.columnconfigure("all", weight=1)
        draw_button = customtkinter.CTkButton(filter_frame,
                                              command=chart_widget.render)
        draw_button.configure(text='Draw')
        draw_button.grid(column=0, row=2,)
        options_frame.grid(column=0, row=1, sticky="nsew")
        options_frame.rowconfigure("all", weight=1)
        options_frame.rowconfigure(4, weight=70)
        options_frame.columnconfigure("all", weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)

        chart_widget.render()
