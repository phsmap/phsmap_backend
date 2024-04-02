acceptable_files = ['all_map_data.txt', 'map_1f.jpg', 'map_2f.jpg', 'map.jpg']
mime_types = ['application/json', 'image/jpeg', 'image/jpeg', 'image/jpeg']
port = 8081
doLog = False

class User:
    def __init__(self, write = [], read = [], create = False, delete = False):
        self.write = write
        self.read = read
        self.create = create
        self.delete = delete