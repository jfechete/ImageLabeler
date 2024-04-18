import sys
import gi
import os
import image
import csv
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio

LEFT_KEY = 65361
RIGHT_KEY = 65363
IMG_KEY = "image"

def main():
    app = MyApp(application_id="com.github.jfechete.ImageLabeler")
    app.run(sys.argv)

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self._main_box)

        self._header = Gtk.HeaderBar()
        self.set_titlebar(self._header)
        self._menu = Gio.Menu.new()
        self._open_dialog = Gtk.FileDialog.new()
        self._open_dialog.set_title("Open folder")
        self._open_button = Gtk.Button(label="Open")
        self._open_button.connect("clicked", lambda _: self.open_folder())
        self._header.pack_start(self._open_button)

        self._labeled_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._labeled_label = Gtk.Label(label="")
        self._labeled_box.append(self._labeled_label)
        self._main_box.append(self._labeled_box)

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

        self._csv_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._csv_export_button = Gtk.Button(label="Export csv file.")
        self._csv_export_button.connect("clicked", self.export_csv)
        self._csv_box.append(self._csv_export_button)
        self._csv_save_dialog = Gtk.FileDialog.new()
        self._csv_save_dialog.set_title("Save csv file")
        csv_filter = Gtk.FileFilter()
        csv_filter.set_name("csv file")
        csv_filter.add_mime_type("text/csv")
        csv_filters = Gio.ListStore.new(Gtk.FileFilter)
        csv_filters.append(csv_filter)
        self._csv_save_dialog.set_filters(csv_filters)
        self._main_box.append(self._csv_box)

        self.keycont = Gtk.EventControllerKey()
        self.keycont.connect("key-pressed", self.handle_keypress)
        self.add_controller(self.keycont)

        loaded = self.load_images()
        if not loaded:
            self.open_folder()

    def open_folder(self):
        self._open_dialog.select_folder(self, None, self._open_callback)

    def _open_callback(self, dialog, result):
        try:
            result = self._open_dialog.select_folder_finish(result).get_path()
            os.chdir(result)
            result = self.load_images()
            if not result:
                self.failed_open()
        except GLib.Error as e:
            pass

    def failed_open(self):
        self._failed_open_dialog = Gtk.AlertDialog()
        self._failed_open_dialog.set_message("Invalid")
        self._failed_open_dialog.set_detail(
            "Invalid folder selected, can't open"
        )
        self._failed_open_dialog.set_modal(True)
        self._failed_open_dialog.set_buttons(["OK"])
        self._failed_open_dialog.choose(
            self, None, self._failed_open_callback
        )

    def _failed_open_callback(self, dialog, result):
        self._failed_open_dialog.choose_finish(result)
        self.open_folder()

    def rotate_right(self):
        self._img_index += 1
        self._img_index = self._img_index%len(self._imgs)
        self.refresh_displayed_image()

    def rotate_left(self):
        self._img_index -= 1
        self._img_index = self._img_index%len(self._imgs)
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
        try:
            self._labels_description = image.ImageLabels.get_labels_description()
        except KeyError as e:
            return False
        self.reload_labels_ui()
        self._imgs = image.get_images(
            labels_description=self._labels_description
        )
        if len(self._imgs) == 0:
            return False
        written = [i.labels.writen for i in self._imgs]
        if all(written):
            self._img_index = 0
        else:
            self._img_index = written.index(False)

        self._csv_save_dialog.set_initial_folder(Gio.File.new_for_path(
            os.getcwd()
        ))
        self.refresh_displayed_image()
        self.update_images_labeled()
        return True

    def export_csv(self, button):
        self._csv_save_dialog.save(self, None, self._export_csv_callback)

    def _export_csv_callback(self, dialog, result):
        try:
            result = self._csv_save_dialog.save_finish(result).get_path()
            if not result.endswith(".csv"):
                result += ".csv"
            fields = list(self._labels_description.keys())
            data = [
                {k:img.labels[k] for k in fields} | {IMG_KEY: img.location}
                for img in self._imgs if img.labels.complete
            ]
            fields = [IMG_KEY] + fields
            with open(result, "w") as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
                csv_writer.writeheader()
                csv_writer.writerows(data)
        except GLib.Error as e:
            pass

    def handle_keypress(self, keycont, keycode, _, modifiers):
        if keycode == LEFT_KEY:
            self.rotate_left()
            return True
        elif keycode == RIGHT_KEY:
            self.rotate_right()
            return True
        return False

    def update_images_labeled(self):
        self._labeled_label.set_text("{}/{} images labeled".format(
            [img.labels.writen for img in self._imgs].count(True),
            len(self._imgs)
        ))

    def _handle_radio_change(self, radio, key, value):
        if radio.get_active():
            self._imgs[self._img_index].labels[key] = value
        self.update_images_labeled()

    def _handle_checkbox_change(self, checbox, key):
        self._imgs[self._img_index].labels[key] = checbox.get_active()
        self.update_images_labeled()

class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

if __name__ == "__main__":
    main()
