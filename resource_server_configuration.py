acceptable_files = ['all_map_data.txt', 'map_1f.jpg', 'map_2f.jpg', 'map.jpg', 'map_wc.jpg', 'placeholder.jpg', 'map_aer.jpg', '2.0_phs_allmap_dev.txt']
mime_types = ['application/json', 'image/jpeg', 'image/jpeg', 'image/jpeg', 'image/jpeg', 'image/jpeg', 'image/jpeg', 'text/plain']
port = 8081
doLog = True
db_acs = []

class User:
    def __init__(self, write = [], read = [], create = False, delete = False):
        self.write = write
        self.read = read
        self.create = create
        self.delete = delete