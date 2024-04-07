import os

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]

class Image:
    def __init__(self, location):
        self._location = location

    @property
    def location(self):
        return self._location

def get_images():
    return [
        Image(file) for file in os.listdir() if any([
            file.lower().endswith("." + e) for e in IMAGE_EXTENSIONS
        ])
    ]
