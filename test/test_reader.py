import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils.reader.FileReader import FileReader


filename = 'test.json'
try:
    reader = FileReader(filename)
    data_str = reader.read()
except Exception as e:
    print('Failed test')
    raise e