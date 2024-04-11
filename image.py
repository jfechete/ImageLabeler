import os
from enum import Enum
import json
import config

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
LABELS_SUFFIX = "_labels.json"

class Image:
    def __init__(self, location, labels_description=None):
        self._location = location
        self._labels = ImageLabels(
            location + LABELS_SUFFIX, labels_description
        )

    @property
    def location(self):
        return self._location

    @property
    def labels(self):
        return self._labels

class ImageLabels:
    @staticmethod
    def get_labels_description():
        label_config  = config.get_config()["labels"]
        labels = {}
        for key in label_config:
            if ":" in label_config[key]:
                label_type, label_info = [
                    t.strip() for t in label_config[key].split(":")
                ]
            else:
                label_type = label_config[key].strip()
                label_info = ""

            if label_type == "bool":
                label_value = {"type":LabelType.BOOL, "default":False}
            elif label_type == "radio":
                label_value = {
                    "type":LabelType.RADIO, "options":[
                        r.strip() for r in label_info.split(",")
                    ]
                }
            labels[key] = label_value
        return labels

    def __init__(self, json_file, description=None):
        if description == None:
            description = ImageLabels.get_labels_description()
        self._description = description

        self._values = {}
        for key, value in self._description.items():
            if "default" in value:
                self._values[key] = value["default"]
        self._json_file = json_file
        if self.writen:
            with open(json_file) as json_fb:
                self._values = json.load(json_fb)

    def __contains__(self, key):
        return key in self._values

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key not in self._description:
            raise ValueError("Unknown key")
        self._values[key] = value

        self.write_if_complete()

    def write_if_complete(self):
        if self.complete:
            with open(self._json_file, "w") as json_fb:
                json.dump(self._values, json_fb)

    @property
    def complete(self):
        complete = True
        for key in self._description:
            if key not in self._values:
                complete = False
        return complete

    @property
    def writen(self):
        return os.path.isfile(self._json_file)

class LabelType(Enum):
    BOOL = 1
    RADIO = 2

def get_images(labels_description=None):
    return [
        Image(file, labels_description=labels_description)
        for file in sorted(os.listdir()) if any([
            file.lower().endswith("." + e) for e in IMAGE_EXTENSIONS
        ])
    ]
