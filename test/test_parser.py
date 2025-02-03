import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils.reader.FileReader import FileReader
from utils.formatter.format import JSONFormat

from utils.controller.dynamic_discover_packages import main_dynamic_discovering
from model.balise import Balise
main_dynamic_discovering()
print(Balise.get_available_balises())

filename = 'test.json'
try:
    reader = FileReader(filename)
    parser: JSONFormat = JSONFormat()

    data_str = reader.read()
    data = parser.parse(data_str)
    print(data)
except Exception as e:
    print('Failed test')
    raise e