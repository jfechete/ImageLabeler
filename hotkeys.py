import config
import image

LEFT_KEY = 65361
RIGHT_KEY = 65363

DEFAULT_KEYS = list("asdfgqwertzxcvb")

def add_hotkeys(labels_description):
    hotkeys_config = config.get_config()["hotkeys"]
    auto_keys = DEFAULT_KEYS.copy()
    for label, label_data in labels_description.items():
        if label_data["type"] == image.LabelType.BOOL:
            if label in hotkeys_config:
                label_data["key"] = hotkeys_config[label]
                auto_keys.remove(label_data["key"] )
            if "key" in label_data:
                continue
            key = auto_keys.pop(0)
            label_data["key"] = key
        elif label_data["type"] == image.LabelType.RADIO:
            if label in hotkeys_config:
                label_data["keys"] = hotkeys_config[label]
                auto_keys = list(filter(
                    lambda x: x not in label_data["keys"], auto_keys
                ))
            if "keys" in label_data:
                continue
            count = len(label_data["options"])
            keys = auto_keys[:count]
            del auto_keys[:count]
            label_data["keys"] = keys

