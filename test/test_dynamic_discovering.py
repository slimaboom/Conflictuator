from utils.controller.dynamic_discover_packages import main_dynamic_discovering
from model.traffic.abstract.ATrafficGeneratorRecorded import ATrafficGeneratorRecorded
from model.traffic.abstract.ATrafficGeneratorDynamic import ATrafficGeneratorDynamic
from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator

main_dynamic_discovering()
print('ATrafficGenerator', ATrafficGenerator.get_available_traffic_generators())
print('ATrafficGeneratorRecorded', ATrafficGeneratorRecorded.get_available_traffic_generators())
print('ATrafficGeneratorDynamic', ATrafficGeneratorDynamic.get_available_traffic_generators())

print('ATrafficGenerator@ATrafficGeneratorRecorded.avail', 
      ATrafficGenerator.get_traffic_generator_class(ATrafficGenerator.get_available_traffic_generators()[0]).get_available_traffic_generators()
)