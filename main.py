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

        self._labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._main_box.append(self._labels_box)

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
        self._main_box.append(self._img_box)

        self.keycont = Gtk.EventControllerKey()
        self.keycont.connect("key-pressed", self.handle_keypress)
        self.add_controller(self.keycont)

        self.load_images()

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

    def reload_labels_ui(self):
        while child := self._labels_box.get_last_child():
            self._labels_box.remove(child)

        for key, label_data in self._labels_description.items():
            label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            if label_data["type"] == image.LabelType.BOOL:
                checkbox = Gtk.CheckButton(label=key)
                label_box.append(checkbox)
            elif label_data["type"] == image.LabelType.RADIO:
                prompt = Gtk.Label(label="{}: ".format(key))
                label_box.append(prompt)

                initial_radio = None
                for option in label_data["options"]:
                    radio_button = Gtk.CheckButton(label=option)
                    if initial_radio == None:
                        initial_radio = radio_button
                    else:
                        radio_button.set_group(initial_radio)
                    label_box.append(radio_button)
            self._labels_box.append(label_box)

    def load_images(self):
        self._labels_description = image.ImageLabels.get_labels_description()
        self.reload_labels_ui()
        self._imgs = image.get_images(
            labels_description=self._labels_description
        )
        self._img_index = 0
        self.refresh_displayed_image()

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
