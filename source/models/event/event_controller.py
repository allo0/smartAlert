# from pulp import *
import random
import time
from datetime import datetime
from typing import Optional

import h3
from firebase_admin import db

from config.appConf import logger
from source.models.event.event_model import EventType, EventsList, Event, EventDetails, SingleEventDetails


def find_users_in_vicinity(location: str, timestamp: int, eventType: EventType) -> list:
    user_list = []
    lat, lon = location.split(",")

    user_ref = db.reference('UserLocation')
    user_snapshot = user_ref.get()

    for key, val in user_snapshot.items():
        print(val)
        lat1, lon1 = val.split(",")

        distance = h3.point_dist([float(lat1), float(lon1)], [float(lat), float(lon)],
                                 unit='m')  # to get distance in meters
        # current_time = datetime.fromtimestamp(time.time())
        ts = datetime.fromtimestamp(timestamp / 1000)  # / 1000
        if distance < circle_radius(val=eventType) \
                and ts.second < time_interval(val=eventType) and key not in user_list:
            user_list.append(key)

    return user_list


def find_events(ref, master_events_list: Optional[list]) -> EventsList:
    if master_events_list:
        events_list = EventsList()
        snapshot = ref.order_by_child('location').get()

        for master_events in master_events_list:
            event = Event()
            match master_events["eventType"]:
                case EventType.FIRE:
                    event.event_type = EventType.FIRE
                    event.master_event_id = master_events["id"]
                    event.master_event_point.append(master_events["location"])
                    event.sub_events = filter_events(master_events, snapshot,
                                                     circle_radius(val=master_events["eventType"]),
                                                     time_interval(val=master_events["eventType"]), event)
                case EventType.EARTHQUAKE:
                    event.event_type = EventType.EARTHQUAKE
                    event.master_event_id = master_events["id"]
                    event.master_event_point.append(master_events["location"])
                    event.sub_events = filter_events(master_events, snapshot,
                                                     circle_radius(val=master_events["eventType"]),
                                                     time_interval(val=master_events["eventType"]), event)
                case EventType.FLOOD:
                    event.event_type = EventType.FLOOD
                    event.master_event_id = master_events["id"]
                    event.master_event_point.append(master_events["location"])
                    event.sub_events = filter_events(master_events, snapshot,
                                                     circle_radius(val=master_events["eventType"]),
                                                     time_interval(val=master_events["eventType"]), event)
                case EventType.OTHER:
                    event.event_type = EventType.OTHER
                    event.master_event_id = master_events["id"]
                    event.master_event_point.append(master_events["location"])
                    event.sub_events = filter_events(master_events, snapshot,
                                                     circle_radius(val=master_events["eventType"]),
                                                     time_interval(val=master_events["eventType"]), event)
                case _:
                    pass
            logger.debug(event)
            #TODO remove it
            event.status_importance=round(random.uniform(0,10), 2)
            events_list.events.append(event)

        logger.info(events_list)
        return events_list


def filter_events(master_events, snapshot, range, time_range, event) -> EventDetails:
    event_details = EventDetails()
    current_time = datetime.fromtimestamp(time.time())

    for key2, val2 in snapshot.items():
        single_event_details = SingleEventDetails()
        # master_events["location"].replace(" ", "")
        lat1, lon1 = master_events["location"].split(",")

        lat2, lon2 = val2["location"].split(",")
        # logger.info('>{0},{1}'.format(lat2, lon2))

        if (lat1, lon1) == (lat2, lon2) or master_events["id"] == val2["id"]:
            continue

        distance = h3.point_dist([float(lat1), float(lon1)], [float(lat2), float(lon2)],
                                 unit='m')  # to get distance in meters

        ts = datetime.fromtimestamp(master_events["timestamp"] / 1000)  # / 1000
        ts2 = datetime.fromtimestamp(val2["timestamp"] / 1000)  # / 1000
        logger.info('{0},{1}'.format(current_time - ts, current_time - ts2))
        first_point = current_time - ts
        # If distance is less than given distance in km calculate event severity
        if master_events["eventType"] == val2["eventType"] and distance < range and first_point.seconds < time_range:
            # logger.info('{0},{1}'.format(val["timestamp"], val2["timestamp"]))
            single_event_details.event_id = val2["id"]
            single_event_details.point.append([lat2, lon2])


        else:
            continue
        if single_event_details.event_id != event.master_event_id:
            event_details.event.append(single_event_details)
    logger.info(event_details)
    return event_details


def find_master_event(ref) -> list:
    mini_master = []
    snapshot = ref.order_by_child('location').get()

    for key, val in snapshot.items():
        lat1, lon1 = val["location"].split(",")

        for key2, val2 in snapshot.items():
            lat2, lon2 = val2["location"].split(",")

            if ((lat1, lon1) == (lat2, lon2)) or (val["id"] == val2["id"]):
                continue

            distance = h3.point_dist([float(lat1), float(lon1)], [float(lat2), float(lon2)],
                                     unit='m')  # to get distance in meters

            # If distance is less than 5 km draw the lines
            if distance < circle_radius(val["eventType"]) and (val["eventType"] == val2["eventType"]):
                if (val not in mini_master) and (val2 not in mini_master):
                    mini_master.append(val)
                break

    logger.info(mini_master)
    return mini_master


def color_marker(val):
    match val:
        case EventType.FIRE:
            return 'red'
        case EventType.EARTHQUAKE:
            return 'darkgreen'
        case EventType.FLOOD:
            return 'blue'
        case EventType.OTHER:
            return 'white'


def circle_radius(val):
    match val:
        case EventType.FIRE:
            return 5000
        case EventType.EARTHQUAKE:
            return 20000
        case EventType.FLOOD:
            return 2000
        case EventType.OTHER:
            return 3000


def time_interval(val):
    match val:
        case EventType.FIRE:
            return 106000
        case EventType.EARTHQUAKE:
            return 106000
        case EventType.FLOOD:
            return 106000
        case EventType.OTHER:
            return 106000
