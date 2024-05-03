"""This file implements the UI.
"""
from pathlib import Path
from itertools import chain
from collections import Counter
from statistics import mean, mode, quantiles, stdev, correlation
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import networkx as nwx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter
from chart import SimpleChartWidget, ChartType, ChartKey
from data import Database, CompiledData
from graph import make_edges
import predictor


class MainForm(customtkinter.CTk):
    """The main form of the application."""
    chart_widget: SimpleChartWidget
    loading_overlay: customtkinter.CTkFrame

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

    def loading(self, is_loading: bool) -> None:
        """Shows/Hides loading overlay."""
        if is_loading:
            self.loading_overlay.grid(row=0, column=0, sticky=tk.NSEW)
            return
        self.loading_overlay.grid_forget()

    def init_components(self) -> None:
        """Initialize each componenents."""
        tab_view = customtkinter.CTkTabview(master=self)
        tab_view.grid(row=0, column=0, sticky=tk.NSEW)
        loading_overlay = customtkinter.CTkFrame(master=self)
        loading_overlay.grid(row=0, column=0, sticky=tk.NSEW)
        progress_bar = customtkinter.CTkProgressBar(master=loading_overlay,
                                                    mode="indeterminate")
        progress_bar.grid(row=0, column=0, sticky=tk.NSEW)
        progress_bar.start()
        loading_label = customtkinter.CTkLabel(master=loading_overlay,
                                               text="Please wait...",
                                               font=("Arial", 48))
        loading_label.grid(row=1, column=0, sticky=tk.NSEW)
        loading_overlay.rowconfigure(0, weight=1, minsize=20)
        loading_overlay.rowconfigure(1, weight=100)
        loading_overlay.columnconfigure("all", weight=1)
        loading_overlay.grid_forget()
        self.loading_overlay = loading_overlay
        for tab_name in ("Chart", "Storytelling", "Graph", "Tree"):
            tab_view.add(tab_name)
        tab_view.set("Chart")
        database = self.load_all_dataset()
        chart_tab = ChartTab(self.loading, tab_view.tab("Chart"), database)
        chart_tab.pack(expand=True, fill=tk.BOTH)
        storytelling_tab = StoryTellingTab(tab_view.tab("Storytelling"),
                                           database)
        storytelling_tab.pack(expand=True, fill=tk.BOTH)
        GraphTab(tab_view.tab("Graph"), database)
        TreeTab(tab_view.tab("Tree"), database)
        self.rowconfigure("all", weight=1)
        self.columnconfigure("all", weight=1)

    def on_chart_type_selected(self, choice) -> None:
        """Fired when the chart type combobox is selected."""
        self.chart_widget.options.chart_type = ChartType.string_to_enum_map(
        )[choice]

    def show(self) -> None:
        """Show the form."""
        self.mainloop()


class TreeTab(customtkinter.CTkFrame):
    """Tree tab
    """

    def __init__(self, parent, database, **kwargs) -> None:
        self.db = database
        self.k_graph, self.table = predictor.initialize(database)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 16))
        style.configure("Treeview", highlightthickness=0, bd=0, font=(None, 16)) # Modify the font of the body
        super().__init__(parent, **kwargs)
        self.init_components()

    def init_components(self) -> None:
        """Initializes the components."""
        tree = ttk.Treeview(master=self, columns=("class",))
        tree.heading("#0", text="Name")
        tree.heading("class", text="Predicted ClassName")
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree.insert(parent='',
                    index=tk.END,
                    iid=0,
                    text="Game",
                    values=("DataModel",))
        tree.bind("<Button-3>", self.popup)
        popup_menu = tk.Menu(self, tearoff=0)
        popup_menu.add_command(
            label="Add",
            command=self.add_node
        )
        popup_menu.add_command(
            label="Destroy",
            command=self.remove_node
        )
        self.popup_menu = popup_menu
        self.tree = tree

    def add_node(self):
        """Add a node."""
        self.tree.insert(parent=self.tree.selection()[0],
            index=tk.END,
            text=tk.simpledialog.askstring("Input Name", "Input the name of the new node: "),
            values=("!PREDICTME",))
        predictor.predict_tree(self.k_graph, self.table, self.tree)

    def remove_node(self):
        """Removes a node."""
        if any(self.tree.parent(select) == '' for select in self.tree.selection()):
            tk.messagebox.showerror("Attempt to delete root", "You cannot delete root!")
            return
        self.tree.delete(self.tree.selection())

    def popup(self, event):
        """On right-click."""
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()


class GraphTab(customtkinter.CTkFrame):
    """Graph tab
    """

    def __init__(self, parent, database, **kwargs):
        self.db = database
        super().__init__(parent, **kwargs)
        self.init_components()

    def render(self, *_):
        """Renders the graph."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        graph_type = self.graph_type_combobox.get()
        graph = nwx.DiGraph()
        if graph_type == "ClassName-ClassName":
            graph.add_nodes_from(
                set(
                    map(
                        lambda val: val.class_name,
                        chain(*map(lambda source: source.everything(),
                                   self.db.sources)))))
            make_edges(graph, self.db.sources, lambda u, v:
                       (u.class_name, v.class_name))
        elif graph_type == "Name-Name":
            graph.add_nodes_from(
                set(
                    map(
                        lambda val: val.name,
                        chain(*map(lambda source: source.everything(),
                                   self.db.sources)))))
            make_edges(graph, self.db.sources, lambda u, v: (u.name, v.name))
        elif graph_type == "ClassName<->Name":
            graph.add_nodes_from(
                set(
                    map(
                        lambda val: val.name,
                        chain(*map(lambda source: source.everything(),
                                   self.db.sources)))))
            graph.add_nodes_from(
                set(
                    map(
                        lambda val: val.class_name,
                        chain(*map(lambda source: source.everything(),
                                   self.db.sources)))))
            make_edges(graph, self.db.sources, lambda u, v:
                       (u.class_name, v.name))
            make_edges(graph, self.db.sources, lambda u, v:
                       (u.name, v.class_name))
        elif graph_type == "Merged Tree":
            graph.add_nodes_from(
                set(
                    map(
                        lambda val: val.class_name + ':' + val.name,
                        chain(*map(lambda source: source.everything(),
                                   self.db.sources)))))
            make_edges(
                graph, self.db.sources, lambda u, v:
                (u.class_name + ':' + u.name, v.class_name + ':' + v.name))
        layout = nwx.kamada_kawai_layout(graph, scale=2)
        nwx.draw_networkx_nodes(graph,
                                layout,
                                node_color='steelblue',
                                node_size=300,
                                ax=ax)
        nwx.draw_networkx_edges(graph, layout, edge_color='gray', ax=ax)
        self.graph_widget.draw()

    def init_components(self):
        """Initializes the components."""
        figure = Figure((6, 6))
        self.figure = figure
        graph_widget = FigureCanvasTkAgg(figure, master=self)
        graph_widget.get_tk_widget().grid(column=0, row=0, sticky="nsew")
        self.graph_widget = graph_widget
        label = customtkinter.CTkLabel(self)
        label.configure(text='Graph Type')
        label.grid(column=0, row=1, sticky="ew")
        graph_type_combobox = customtkinter.CTkComboBox(
            self,
            values=("ClassName-ClassName", "Name-Name", "ClassName<->Name",
                    "Merged Tree"),
            command=self.render)
        graph_type_combobox.set("ClassName-ClassName")
        graph_type_combobox.grid(column=0, row=2, sticky="ew")
        self.graph_type_combobox = graph_type_combobox
        self.pack(side="top", expand=True, fill=tk.BOTH)
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, minsize=20, weight=1)
        self.columnconfigure(0, minsize=20, weight=1)
        self.render()


class StoryTellingTab(customtkinter.CTkFrame):
    """Story telling tab.
    """
    db: Database
    chart_combobox: customtkinter.CTkComboBox
    left_desc: customtkinter.CTkComboBox
    right_desc: customtkinter.CTkComboBox

    def __init__(self, parent, database, **kwargs):
        self.db = database
        super().__init__(parent, **kwargs)
        self.init_components()

    def render(self, *_):
        """Render everything."""
        proc_map = {
            "Name Length":
            lambda val: len(val.name),
            "Class Name Length":
            lambda val: len(val.class_name),
            "Depth":
            lambda val: val.depth(),
            "Number of Children":
            lambda val: len(val.children) if val.children else 0,
        }
        left_proc = proc_map[self.left_desc.get()]
        right_proc = proc_map[self.right_desc.get()]
        # Convert to list so we can use it multiple times.
        # idc if we use more memory, let the os handle that shit.
        # It's better than having to process all the data again.
        left_data = list(
            map(
                left_proc,
                chain(*map(lambda source: source.everything(),
                           self.db.sources))))
        right_data = list(
            map(
                right_proc,
                chain(*map(lambda source: source.everything(),
                           self.db.sources))))
        quantile = quantiles(left_data)
        self.left_mean_label.configure(
            text=f"Mean: {mean(left_data)}\n"
            f"Median: {quantile[1]}\n"
            f"Mode: {mode(left_data)}\n"
            f"First quantile: {quantile[0]}\n"
            f"Third quantile: {quantile[2]}\n"
            f"Standard Deviation: {stdev(left_data)}")
        quantile = quantiles(right_data)
        self.right_mean_label.configure(
            text=f"Mean: {mean(right_data)}\n"
            f"Median: {quantile[1]}\n"
            f"Mode: {mode(right_data)}\n"
            f"First quantile: {quantile[0]}\n"
            f"Third quantile: {quantile[2]}\n"
            f"Standard Deviation: {stdev(right_data)}")
        self.corr_label.configure(
            text=f"Correlation: {correlation(left_data, right_data)}")
        chart_type = self.chart_combobox.get()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if chart_type == "Depth Class Name Count Stacked Bar Graph":
            counter = Counter()
            for v in chain(
                    *map(lambda source: source.everything(), self.db.sources)):
                counter[v.depth()] += 1
            depths = counter.keys()
            counter = Counter()
            for v in chain(
                    *map(lambda source: source.everything(), self.db.sources)):
                counter[v.class_name] += 1
            common_classnames = [val[0] for val in counter.most_common(9)]
            counter = Counter()
            for v in chain(
                    *map(lambda source: source.everything(), self.db.sources)):
                counter[(v.class_name if v.class_name in common_classnames else
                         "Other", v.depth())] += 1

            color_arr = ("#FF0000", "#0000FF", "#F58231", "#FFFF00", "#BFEF45",
                         "#3CB44B", "#00FFFF", "#911EB4", "#F032E6", "#A9A9A9")
            bottom = np.zeros(len(depths))
            common_classnames.append("Other")
            for i, cc in enumerate(common_classnames):
                new_counter = Counter()
                for k, v in counter.items():
                    if k[0] != cc:
                        continue
                    new_counter[k[1]] += v
                vals = [new_counter[depth] for depth in depths]
                ax.bar(range(len(depths)),
                       vals,
                       label=cc,
                       color=color_arr[i],
                       bottom=bottom)
                bottom += vals
            ax.set_xticks(range(len(depths)), depths)
            ax.legend(loc='upper right', ncols=5)
            ax.set_title("Number of Instances at different depths")
            ax.set_xlabel("Depth")
            ax.set_ylabel("Number of Instances")
            self.chart_widget.draw()
            return
        if chart_type == "Scatter Plot":
            ax.scatter(left_data, right_data)
            ax.set_xlabel(self.left_desc.get())
            ax.set_ylabel(self.right_desc.get())
            self.chart_widget.draw()
            return

    def init_components(self):
        """Initialize the widgets."""
        figure = Figure((6, 6))
        self.figure = figure
        chart_widget = FigureCanvasTkAgg(figure, master=self)
        chart_widget.get_tk_widget().grid(column=0, row=0, sticky="nsew")
        self.chart_widget = chart_widget
        settings = customtkinter.CTkFrame(self)
        settings.configure(height=200, width=200)
        chart_frame = customtkinter.CTkFrame(settings)
        chart_combobox = customtkinter.CTkComboBox(
            chart_frame,
            state="readonly",
            command=self.render,
            values=("Depth Class Name Count Stacked Bar Graph",
                    "Scatter Plot"))
        chart_combobox.set("Depth Class Name Count Stacked Bar Graph")
        chart_combobox.grid(column=0, row=1, sticky="ew")
        self.chart_combobox = chart_combobox
        preset_label = customtkinter.CTkLabel(chart_frame)
        preset_label.configure(text='Choose storytelling graph')
        preset_label.grid(column=0, row=0, sticky="nsew")
        chart_frame.grid(column=0, row=0, sticky="nsew")
        chart_frame.rowconfigure("all", weight=1)
        chart_frame.columnconfigure("all", weight=1)
        desc_frame = customtkinter.CTkFrame(settings)
        attributes = ("Name Length", "Class Name Length", "Depth",
                      "Number of Children")
        left_desc = customtkinter.CTkComboBox(desc_frame,
                                              values=attributes,
                                              state="readonly",
                                              command=self.render)
        left_desc.set(attributes[0])
        left_desc.grid(column=0, columnspan=1, row=0, sticky="ew")
        self.left_desc = left_desc
        right_desc = customtkinter.CTkComboBox(desc_frame,
                                               values=attributes,
                                               state="readonly",
                                               command=self.render)
        right_desc.set(attributes[1])
        right_desc.grid(column=1, row=0, sticky="ew")
        self.right_desc = right_desc
        left_mean_label = customtkinter.CTkLabel(desc_frame)
        left_mean_label.configure(justify="left", text='Mean')
        left_mean_label.grid(column=0, row=1, sticky="nsew")
        self.left_mean_label = left_mean_label
        right_mean_label = customtkinter.CTkLabel(desc_frame)
        right_mean_label.configure(text='Mean')
        right_mean_label.grid(column=1, row=1, sticky="nsew")
        self.right_mean_label = right_mean_label
        corr_label = customtkinter.CTkLabel(desc_frame)
        corr_label.configure(text='Correlation:')
        corr_label.grid(column=0, columnspan=2, row=2)
        self.corr_label = corr_label
        desc_frame.grid(column=1, columnspan=1, row=0, sticky="nsew")
        desc_frame.rowconfigure("all", weight=1)
        desc_frame.columnconfigure("all", weight=1)
        settings.grid(column=0, row=1, sticky="nsew")
        settings.rowconfigure("all", weight=1)
        settings.columnconfigure("all", weight=1)
        self.pack(expand=True, fill="both", side="top")
        self.rowconfigure(0, weight=7)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.render()


class ChartTab(customtkinter.CTkFrame):
    """The chart tab."""
    db: Database
    compiled_data: CompiledData
    chart_widget: SimpleChartWidget
    chart_type_combobox: customtkinter.CTkComboBox
    show_others_checkbox: customtkinter.CTkCheckBox
    filter_entries_frame: customtkinter.CTkScrollableFrame
    highest_count_string: tk.StringVar
    chart_title_string: tk.StringVar
    chart_x_axis_title_string: tk.StringVar
    chart_y_axis_title_string: tk.StringVar
    filters: set[tk.StringVar]
    key_type: ChartKey
    filtered_sources: set
    data_dirty: bool

    def __init__(self, loading, parent, database, **kwargs):
        self.db = database
        self.loading = loading
        self.data_dirty = False
        self.filters = []
        self.filtered_sources = set()
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
        self.chart_widget.options.chart_type = ChartType.string_to_enum_map(
        )[choice]

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
        self.data_dirty = True

    def on_filter_source(self, path, widget):
        """Fires when source filter state is changed."""
        if widget.get():
            self.filtered_sources.remove(path)
        else:
            self.filtered_sources.add(path)
        self.data_dirty = True

    def on_draw(self):
        """Fires when the draw button is pressed."""
        self.loading(True)
        if self.data_dirty:
            counter = tk.IntVar(value=0)

            # GIL messing the shit up freezing it anyways, gotta do this dirty shit.
            def pre_up(counter=counter):
                val = counter.get()
                counter.set(counter.get() + 1)
                if val % 20000 == 0:
                    self.update()

            try:
                self.compiled_data.compile(
                    (source for source in self.db.sources
                     if source.source_path not in self.filtered_sources),
                    self.key_type.value,
                    lambda val, eval_text=(
                        (' and '.join('(' + fil.get() + ')'
                                      for fil in self.filters))
                        if self.filters else None): pre_up() or
                    (eval(eval_text) if eval_text else True))
            except Exception as error:
                tk.messagebox.showerror("Error", error)
        self.chart_widget.render()
        self.loading(False)

    def on_add_filter(self):
        """Fires when the add filter button is pressed."""
        entry_text = tk.StringVar(value="True")
        entry = customtkinter.CTkEntry(self.filter_entries_frame,
                                       textvariable=entry_text)

        def value_changed(*_, text=entry_text, widget=entry):
            code = text.get()
            if code == '-':
                self.filters.remove(text)
                self.after(0, widget.destroy)

        self.filters.append(entry_text)
        entry_text.trace('w', value_changed)
        entry.pack(anchor=tk.N, expand=True, fill=tk.X)

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
        add_filter_btn = customtkinter.CTkButton(filter_frame,
                                                 text="Add Filter",
                                                 command=self.on_add_filter)
        add_filter_btn.grid(row=1, column=0, sticky=tk.NSEW)
        filter_entries_frame = customtkinter.CTkScrollableFrame(filter_frame)
        filter_entries_frame.grid(column=0, row=2, sticky="nsew")
        self.filter_entries_frame = filter_entries_frame
        filter_frame.grid(column=0, columnspan=2, row=4, sticky="nsew")
        filter_frame.rowconfigure(0, minsize=20, weight=100)
        filter_frame.rowconfigure(1, minsize=20, weight=100)
        filter_frame.rowconfigure(2, weight=1)
        filter_frame.columnconfigure(0, weight=1)

        data_sources_frame = customtkinter.CTkFrame(options_frame)
        data_source_entries = customtkinter.CTkScrollableFrame(
            data_sources_frame)
        data_source_entries.grid(column=0, row=1, sticky="nsew")
        for source in self.db.sources:
            entry = customtkinter.CTkCheckBox(data_source_entries,
                                              text=source.source_path.name)
            entry.configure(command=lambda path=source.source_path, widget=
                            entry: self.on_filter_source(path, widget))
            entry.select()
            entry.pack(expand=True, side=tk.TOP, fill=tk.X, padx=10, pady=5)
        label9 = customtkinter.CTkLabel(data_sources_frame)
        label9.configure(anchor="center", text='Sources')
        label9.grid(column=0, row=0, sticky="nsew")
        data_sources_frame.grid(column=2, row=4, columnspan=2, sticky="nsew")
        data_sources_frame.rowconfigure(0, weight=100, minsize=20)
        data_sources_frame.rowconfigure(1, weight=1)
        data_sources_frame.columnconfigure(0, weight=1)
        draw_button = customtkinter.CTkButton(options_frame,
                                              command=self.on_draw)
        draw_button.configure(text='Draw')
        draw_button.grid(column=0, row=5, columnspan=4)
        options_frame.grid(column=0, row=1, sticky="nsew")
        options_frame.rowconfigure("all", weight=1)
        options_frame.rowconfigure(3, minsize=40)
        options_frame.rowconfigure(4, weight=70)
        options_frame.columnconfigure("all", weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)

        self.on_draw()
