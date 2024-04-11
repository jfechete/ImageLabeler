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
        self._labels_widgets = {}
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

        for key, data in self._labels_description.items():
            if data["type"] == image.LabelType.BOOL:
                if key in self._imgs[self._img_index].labels:
                    self._labels_widgets[key].set_active(
                        self._imgs[self._img_index].labels[key]
                    )
                else:
                    self._labels_widgets[key].set_active(False)
            elif data["type"] == image.LabelType.RADIO:
                if key in self._imgs[self._img_index].labels:
                    self._labels_widgets[key][
                        self._imgs[self._img_index].labels[key]
                    ].set_active(True)
                else:
                    for radio_button in self._labels_widgets[key].values():
                        radio_button.set_active(False)
        self._imgs[self._img_index].labels.write_if_complete()

    def reload_labels_ui(self):
        while child := self._labels_box.get_last_child():
            self._labels_box.remove(child)
        self._labels_widgets.clear()

        for key, label_data in self._labels_description.items():
            label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            if label_data["type"] == image.LabelType.BOOL:
                checkbox = Gtk.CheckButton(label=key)
                checkbox.connect("toggled", self._handle_checkbox_change, key)
                self._labels_widgets[key] = checkbox
                label_box.append(checkbox)
            elif label_data["type"] == image.LabelType.RADIO:
                prompt = Gtk.Label(label="{}: ".format(key))
                self._labels_widgets[key] = {}
                label_box.append(prompt)

                initial_radio = None
                for option in label_data["options"]:
                    radio_button = Gtk.CheckButton(label=option)
                    if initial_radio == None:
                        initial_radio = radio_button
                    else:
                        radio_button.set_group(initial_radio)
                    radio_button.connect(
                        "toggled", self._handle_radio_change, key, option
                    )
                    self._labels_widgets[key][option] = radio_button
                    label_box.append(radio_button)
            self._labels_box.append(label_box)

    def load_images(self):
        self._labels_description = image.ImageLabels.get_labels_description()
        self.reload_labels_ui()
        self._imgs = image.get_images(
            labels_description=self._labels_description
        )
        written = [i.labels.writen for i in self._imgs]
        if all(written):
            self._img_index = 0
        else:
            self._img_index = written.index(False)
        self.refresh_displayed_image()

    def handle_keypress(self, keycont, keycode, _, modifiers):
        if keycode == LEFT_KEY:
            self.rotate_left()
            return True
        elif keycode == RIGHT_KEY:
            self.rotate_right()
            return True
        return False

    def _handle_radio_change(self, radio, key, value):
        if radio.get_active():
            self._imgs[self._img_index].labels[key] = value

    def _handle_checkbox_change(self, checbox, key):
        self._imgs[self._img_index].labels[key] = checbox.get_active()

class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

if __name__ == "__main__":
    main()
