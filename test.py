from model.traffic.concrete.TrafficGeneratorRecorded import TrafficGeneratorRecorded
from model.traffic.concrete.TrafficGeneratorDynamic import TrafficGeneratorDynamic

from model.traffic.abstract.ATrafficGeneratorRecorded import ATrafficGeneratorRecorded
from model.traffic.abstract.ATrafficGeneratorDynamic import ATrafficGeneratorDynamic
from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator

print('ATrafficGenerator', ATrafficGenerator.get_available_traffic_generators())
print('ATrafficGeneratorRecorded', ATrafficGeneratorRecorded.get_available_traffic_generators())
print('ATrafficGeneratorDynamic', ATrafficGeneratorDynamic.get_available_traffic_generators())

print('ATrafficGenerator@ATrafficGeneratorRecorded.avail', 
      ATrafficGenerator.get_traffic_generator_class(ATrafficGenerator.get_available_traffic_generators()[0]).get_available_traffic_generators()
)