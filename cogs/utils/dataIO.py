from random import randint
from json import decoder, dump, load
from os import replace

class DataIO():

    def save_json(self, filename, data):
        """Atomically saves json file"""
        path, ext = splitext(filename)
        tmp_file = "{}.{}.tmp".format(path, randint(1000, 9999))
        with open(tmp_file, 'w', encoding='utf-8') as f:
            dump(data, f, indent=4,sort_keys=True,separators=(',',' : '))
        try:
            with open(tmp_file, 'r', encoding='utf-8') as f:
                data = load(f)
        except decoder.JSONDecodeError:
            print("Attempted to write file {} but JSON "
                                  "integrity check on tmp file has failed. "
                                  "The original file is unaltered."
                                  "".format(filename))
            return False
        except Exception as e:
            print('A issue has occured saving the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return False
            
        replace(tmp_file, filename)
        return True

    def load_json(self, filename):
        """Loads json file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = load(f)
            return data
        except Exception as e:
            print('A issue has occured loading the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return {}
        
    def append_json(self, filename, data):
		"""Appends to json file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file = load(f)
        except Exception as e:
            print('A issue has occured loading the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return False
        try:
            file.append(data)
        except Exception as e:
            print('A issue has occured updating the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return False
                path, ext = splitext(filename)
        tmp_file = "{}.{}.tmp".format(path, randint(1000, 9999))
        with open(tmp_file, 'w', encoding='utf-8') as f:
            dump(file, f, indent=4,sort_keys=True,separators=(',',' : '))
        try:
            with open(tmp_file, 'r', encoding='utf-8') as f:
                data = load(f)
        except decoder.JSONDecodeError:
            print("Attempted to write file {} but JSON "
                                  "integrity check on tmp file has failed. "
                                  "The original file is unaltered."
                                  "".format(filename))
            return False
        except Exception as e:
            print('A issue has occured saving the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return False
            
        replace(tmp_file, filename)
        return True
        
    def is_valid_json(self, filename):
        """Verifies if json file exists / is readable"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = load(f)
            return True
        except (FileNotFoundError, decoder.JSONDecodeError):
            return False
        except Exception as e:
            print('A issue has occured validating the Json.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(e.message, e.args))
            return False

dataIO = DataIO()
