import os
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # Create a Builder
        builder = Gtk.Builder()
        builder.add_from_file("inkput.ui")

        # Obtain and show the main window
        self.win = builder.get_object("main_window")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.present()

        # Obtain the button widget and connect it to a function
        button = builder.get_object("predictbutton")
        button.connect("clicked", self.hello)

        self.drawing_area = builder.get_object("drawing_area")
        self.drawing_area.set_draw_func(self.draw, None)

        self.drawing_area.set_cursor(Gdk.Cursor.new_from_name("none"))

        evk = Gtk.EventControllerMotion.new()
        evk.connect("motion", self.mouse_motion)
        self.drawing_area.add_controller(evk)

        evk = Gtk.GestureClick.new()
        evk.connect("pressed", self.set_pendown_state, True)
        evk.connect("released", self.set_pendown_state, False)
        self.drawing_area.add_controller(evk)

        self.blobs = []
        self.pendown_state = False


    def set_pendown_state(self, gesture, data, x, y, pen_status):
        self.pendown_state = pen_status
        print("pen down" if pen_status else "pen up")

        if pen_status == False: # pen up
            self.drawing_area.queue_draw()
            print(len(self.blobs))

        
    def mouse_motion(self, motion, x, y):
        if self.pendown_state:
            self.blobs.append((x, y))
            #self.drawing_area.queue_draw() # not drawing here 'cause its sloow
            #print(f"Mouse moved to {x}, {y}")

    def draw(self, area, c, w, h, data):
        # c is a Cairo context

        # Fill background
        c.set_source_rgb(1, 1, 1)
        c.paint()

        c.set_source_rgb(0, 0, 0)
        for x, y in self.blobs:
            c.arc(x, y, 2, 0, 2 * 3.1415926)
            c.fill()

    def hello(self, button):
        print("drawing")
        self.drawing_area.queue_draw()

app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
