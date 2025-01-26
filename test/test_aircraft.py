import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator.traffic_generator import AIRCRAFTS
from logging_config import setup_logging
from model.utils import sec_to_time

logger = setup_logging(__file__.split("/")[-1])

for id, aircraft in AIRCRAFTS.get_all().items():
    aircraft.calculate_estimated_times_commands()
    
    fpt = aircraft.get_flight_plan_timed()
    fpt = {k: f"{v} ({sec_to_time(v)})" for k,v in fpt.items()}
    msg = f"\nAircraft Id: {id}\nFlightPlanTimed:\n{fpt}\n\n"

    logger.info(msg)