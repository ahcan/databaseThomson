class File:
    def __init__(self):
        self.file_path = 'setting/'

    def read(self, filename):
        #print self.file_path + filename
        f = open(self.file_path + filename , 'r')
        lines=f.read()
        f.close()
        #return data
        return lines

    def append(self, filename, text):
        f = open(self.file_path + filename, 'a')
        f.write(text+"\n")
        f.close()

    def get_response(self, filename):
        response = self.read(filename)
        return response