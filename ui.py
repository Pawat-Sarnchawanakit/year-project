import tkinter as tk
from pathlib import Path
from itertools import chain
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter
from data import Database

class MainForm(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Project")
        fig = Figure(figsize=(6, 6))
        db = Database()
        for file in Path("./dataset/").iterdir():
            if not file.is_file():
                continue
            db.add_source(file)
        # bucket = Counter(map(lambda val: val.class_name, filter(lambda val: not any(map(lambda ancestor: ancestor.class_name == "Model", val.ancestors())), chain(*map(lambda source: source.everything(), db.sources)))))
        # bucket = Counter(map(lambda val: val.class_name, filter(lambda val: sum(1 for _ in val.ancestors()) == 10, chain(*map(lambda source: source.everything(), db.sources)))))
        bucket = Counter(map(lambda val: val.name, chain(*db))).most_common(32)
        # bucket = Counter(map(lambda val: val.depth(), chain(*db))).items()
        
        # bucket = dict(
        #     sorted(bucket.items(), key=lambda item: item[1],
        #            reverse=True)[:50])
        self.bucket = bucket
        print(bucket)
        plt = fig.add_subplot(111)
        ticks = range(len(bucket))
        plt.barh(ticks, [val[1] for val in bucket])
        plt.set_yticks(ticks, [val[0] for val in bucket])
        canvas = FigureCanvasTkAgg(
            fig, master=self)  # Convert the Figure to a tkinter widget
        canvas.get_tk_widget().grid(sticky=tk.NSEW)
        canvas.draw()
        self.canvas = canvas
        self.plt = plt
        chart_type_combobox = customtkinter.CTkComboBox(self, values=("Histogram", "Pie"), command=self.on_chart_type_selected)
        chart_type_combobox.grid(row=1, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def on_chart_type_selected(self, choice):
        plt = self.plt
        plt.clear()
        plt.pie([val[1] for val in self.bucket], labels=[val[0] for val in self.bucket])
        self.canvas.draw()

    def show(self):
        self.mainloop()
