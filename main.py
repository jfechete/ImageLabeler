import sys
import gi
import os
import image
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

LEFT_KEY = 65361
RIGHT_KEY = 65363

def main():
    app = MyApp(application_id="com.github.jfechete.ImageLabeler")
    app.run(sys.argv)

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self._main_box)

        self._img_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._img_box.set_vexpand(True)
        self._current_img_label = Gtk.Picture()
        self._previous_img_label = Gtk.Picture()
        self._next_img_label = Gtk.Picture()
        self._previous_img_button = Gtk.Button(child=self._previous_img_label)
        self._previous_img_button.connect(
            "clicked", lambda _: self.rotate_left()
        )
        self._next_img_button = Gtk.Button(child=self._next_img_label)
        self._next_img_button.connect(
            "clicked", lambda _: self.rotate_right()
        )
        self._img_box.append(self._previous_img_button)
        self._img_box.append(self._current_img_label)
        self._img_box.append(self._next_img_button)
        self.load_images()
        self.refresh_displayed_image()
        self._main_box.append(self._img_box)

        self.keycont = Gtk.EventControllerKey()
        self.keycont.connect("key-pressed", self.handle_keypress)
        self.add_controller(self.keycont)

    def rotate_right(self):
        self._img_index += 1
        self.refresh_displayed_image()

    def rotate_left(self):
        self._img_index -= 1
        self.refresh_displayed_image()

    def refresh_displayed_image(self):
        self._previous_img_label.set_filename(self._imgs[
            (self._img_index-1)%len(self._imgs)
        ].location)
        self._current_img_label.set_filename(self._imgs[
            self._img_index%len(self._imgs)
        ].location)
        self._next_img_label.set_filename(self._imgs[
            (self._img_index+1)%len(self._imgs)
        ].location)

    def load_images(self):
        self._imgs = image.get_images()
        self._img_index = 0

    def handle_keypress(self, keycont, keycode, _, modifiers):
        if keycode == LEFT_KEY:
            self.rotate_left()
            return True
        elif keycode == RIGHT_KEY:
            self.rotate_right()
            return True
        return False

class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

if __name__ == "__main__":
    main()
