import gi
gi.require_version("Ide", "1.0")
import os
from gi.repository import GObject
from gi.repository import Ide
from gi.repository import Gtk
from gi.repository import Gdk
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo \
        import FigureCanvasGTK3Cairo as FigCanvas
import numpy as np
import threading
import time


class MainPlugin(GObject.Object, Ide.WorkbenchAddin):

    """
    Main class of the plugin.

    Handles the loading and unloading of the plugin.
    """

    def do_load(self, workbench):
        self.workbench = workbench
        context = self.workbench.props.context
        vcs = context.get_vcs()
        workdir = vcs.get_working_directory().get_path()
        self.perspective = StatPerspective(workdir, visible=True)
        self.workbench.add_perspective(self.perspective)

    def do_unload(self, app):
        self.workbench = None


class StatPerspective(Gtk.Box, Ide.Perspective):

    """
    Sets up the stats perspective and handles the signals.

    This class sets up the containers of the perspective
    and the matplotlib figure and canvas. An asynchronous
    method iterates over the project and gathers the data
    for the plot.
    """

    def __init__(self, workdir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workdir = workdir

        # main containers
        scr_win = Gtk.ScrolledWindow(visible=True)
        pad_box = Gtk.Box(visible=True)
        pad_box.pack_start(scr_win, True, True, 20)

        main_box = Gtk.Box(visible=True, orientation=Gtk.Orientation.VERTICAL)
        scr_win.add_with_viewport(main_box)

        # content
        lbl_head = '<span font="36.0"><b>Project Stats</b></span>'
        heading = Gtk.Label(label=lbl_head, expand=True, visible=True)
        heading.set_use_markup(True)
        main_box.pack_start(heading, False, False, 0)
        line = Gtk.Separator(visible=True)
        main_box.pack_start(line, False, False, 0)

        self.fig = Figure(facecolor='none')
        self.ax = self.fig.add_subplot(111, axisbg='#ffffff')
        self.canvas = FigCanvas(self.fig)
        self.canvas.set_size_request(800, 600)
        self.canvas.draw()
        self.canvas.show()
        main_box.pack_start(self.canvas, True, True, 0)

        self.add(pad_box)
        self.titlebar = Ide.WorkbenchHeaderBar(visible=True)

         # Gather stats
        thread = threading.Thread(target=self.gather_stats)
        thread.daemon = True
        thread.start()

    def gather_stats(self):
        file_types = {}

        for root, subfolders, files in os.walk(self.workdir):
            for file in files:
                try:
                    with open(root + "/" + file) as fl:
                        line_count = 0
                        for line in fl:
                            line_count += 1

                        splt_str = file.split(".")
                        if len(splt_str) > 1:
                            file_ext = splt_str[-1]
                        else:
                            continue
                        if file_ext in file_types:
                            # key exists, add line count
                            file_types[file_ext] = file_types[file_ext] + line_count
                        else:
                            # key doesn't exist, create new key
                            file_types[file_ext] = line_count
                except:
                    continue

        keys = []
        values = []

        for key, value in file_types.items():
            keys.append(key)
            values.append(value)

        key_ar = np.array(keys)
        val_ar = np.array(values).astype(int)

        ar = np.vstack((key_ar, val_ar)).T
        ar = ar[ar[:,1].astype(int).argsort()]
        rows = ar.shape[0]
        val_pos = np.arange(1, ar.shape[0]+1)

        self.ax.barh(val_pos, ar[:,1].astype(int), 0.8, align="center")
        # facecolor='yellow'
        self.ax.set_yticks(val_pos)
        self.ax.tick_params(axis="both", which="major", pad=15)
        self.ax.set_yticklabels(ar[:,0], fontsize="16", weight="bold")
        self.ax.tick_params(axis="x", which="major", labelsize="16")

        self.canvas.set_size_request(800, (rows * 20 + 50))
        self.canvas.draw()

    def do_get_id(self):
        return 'hello-world2'

    def do_get_title(self):
        return 'Hello'

    def do_get_priority(self):
        return 10000

    def do_get_icon_name(self):
        return "utilities-system-monitor-symbolic"

    def do_get_titlebar(self):
        return self.titlebar

