from json import load, dump, decoder
from os import replace
from random import randint

class DataIO():

    def save_json(self, filename, data):
        """Atomically saves json file"""
        rnd = randint(1000, 9999)
        path, ext = splitext(filename)
        tmp_file = "{}-{}.tmp".format(path, rnd)
        with open(tmp_file, encoding='utf-8', mode="w") as f:
            dump(data, f, indent=4,sort_keys=True,
                separators=(',',' : '))
        try:
            with open(tmp_file, encoding='utf-8', mode="r") as f:
                data = load(f)
        except decoder.JSONDecodeError:
            self.logger.exception("Attempted to write file {} but JSON "
                                  "integrity check on tmp file has failed. "
                                  "The original file is unaltered."
                                  "".format(filename))
            return False
        replace(tmp_file, filename)
        return True

    def load_json(self, filename):
        """Loads json file"""
        with open(filename, encoding='utf-8', mode="r") as f:
            data = load(f)
        return data

    def is_valid_json(self, filename):
        """Verifies if json file exists / is readable"""
        try:
            with open(filename, encoding='utf-8', mode="r") as f:
                data = load(f)
            return True
        except FileNotFoundError:
            return False
        except decoder.JSONDecodeError:
            return False

dataIO = DataIO()
