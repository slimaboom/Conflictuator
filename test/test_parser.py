import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils.reader.FileReader import FileReader
from utils.formatter.format import JSONFormat

filename = 'test.json'
try:
    reader = FileReader(filename)
    parser: JSONFormat = JSONFormat()

    data_str = reader.read()
    data = parser.parse(data_str)
    print(data[0][2])
except Exception as e:
    print('Failed test')
    raise e