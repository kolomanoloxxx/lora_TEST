class LogWriter(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, 'wt')
        self.file.close()

    def new(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, 'wt')
        self.file.close()

    def add(self, file_name, data):
        self.file = open(self.file_name, 'at')
        self.file.write(data)
        self.file.close()
 
