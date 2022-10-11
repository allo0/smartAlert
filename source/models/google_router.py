import json

import aiohttp
import folium
# from pulp import *
import h3
import pandas as pd
from fastapi import APIRouter, Depends, Request
from firebase_admin import db
from folium.plugins import MarkerCluster
from starlette.responses import HTMLResponse

from config.appConf import logger, Settings
from source.models.auth.auth_controller import get_user
from source.models.event.event_controller import find_master_event, color_marker, circle_radius, find_events, \
    find_users_in_vicinity
from source.models.event.event_model import CreateEvent, EventType
from source.models.firebase.firebase_models import FirebaseConfig
from source.models.user.user_model import GoogleEmailRequest, GoogleEmailSignin

backendGoogleRouter = APIRouter(
    tags=["Firebase backend APIs functionality"],
    responses={200: {"description": "Response Successfull"},
               422: {"description": "Validation Error"}
               },
)

ref = FirebaseConfig().reference


@backendGoogleRouter.post("/login", summary="Only exists for backend idToken generation ")
async def login(info: GoogleEmailRequest):
    req_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + Settings.GOOGLE_API_KEY

    headers_list = {
        "Accept": "*/*",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "email": info.email,
        "password": info.password,
        "returnSecureToken": info.returnSecureToken
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(req_url, data=payload, headers=headers_list) as resp:
            try:
                obj = await resp.json()
                logger.debug(obj)

                return GoogleEmailSignin(kind=obj["kind"], localId=obj["localId"],
                                         displayName=obj["displayName"], registered=obj["registered"],
                                         refreshToken=obj["refreshToken"], expiresIn=obj["expiresIn"],
                                         idToken=obj["idToken"], email=obj["email"])

            except Exception as e:
                return await resp.json()


@backendGoogleRouter.get("/idToken", summary="Only exists for backend confirmation")
async def hello_user(user=Depends(get_user)):
    return {"idToken": user}


@backendGoogleRouter.get("/userInfo", dependencies=[Depends(get_user)], summary="Only exists for backend purposes")
async def user_info(id_token: str):
    req_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + Settings.GOOGLE_API_KEY

    headers_list = {
        "Accept": "*/*",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "idToken": id_token
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(req_url, data=payload, headers=headers_list) as resp:
            try:
                obj = await resp.json()
                logger.debug(obj)

                return obj

            except Exception as e:
                return await resp.json()


@backendGoogleRouter.post("/event", summary="Only exists for backend Create Events on map")
async def create_event(event: CreateEvent):
    logger.info(event.json())
    ref = db.reference('Events')
    new_event = ref.push()
    new_event.set({
        'activated': event.activated,
        'comments': event.comments,
        'eventImage': event.eventImage,
        'eventType': event.eventType,
        'id': event.id,
        'location': event.location,
        'timestamp': event.timestamp,
        'userEmail': event.userEmail
    })
    # ref.set(event.json())
    return event


@backendGoogleRouter.get("/users_in_vicinity")
async def users_in_vicinity(location: str, timestamp: int, eventType: EventType):
    return find_users_in_vicinity(location=location, timestamp=timestamp, eventType=eventType)


@backendGoogleRouter.get("/incident_severity")
async def incident_severity():
    master_events_list = find_master_event(ref=ref)
    return find_events(ref=ref, master_events_list=master_events_list)


@backendGoogleRouter.get("/incident_map", response_class=HTMLResponse)
async def incident_map(request: Request):
    m = folium.Map(location=(36.9540700, 24.7360300), zoom_start=6)
    user_location = MarkerCluster(name="UserLocation", overlay=True)
    marker_cluster = MarkerCluster(name="Events", overlay=True)
    radius_layer = folium.FeatureGroup(name="Radius", overlay=True)
    distance_layer = folium.FeatureGroup(name="Distance", overlay=True)

    tooltip = "More info"

    # Add Events on the map
    ref = db.reference('Events')
    snapshot = ref.order_by_child('location').get()
    for key, val in snapshot.items():
        lat1, lon1 = val["location"].split(",")
        logger.info('{0},{1}'.format(lat1, lon1))

        folium.Marker(
            val["location"].split(","),
            popup="<i>" + val["comments"] + "</i>",
            tooltip=tooltip,
            icon=folium.Icon(color=color_marker(val=val["eventType"]))
        ).add_to(marker_cluster)

        folium.Circle(
            location=val["location"].split(","),
            radius=circle_radius(val=val["eventType"]),
            color=color_marker(val=val["eventType"]),
            # fill=True,
            # fill_color="#3186cc",
        ).add_to(radius_layer)

        for key2, val2 in snapshot.items():
            lat2, lon2 = val2["location"].split(",")
            logger.info('>{0},{1}'.format(lat2, lon2))

            if ((lat1, lon1) == (lat2, lon2)) or (val["id"] == val2["id"]):
                continue

            distance = h3.point_dist([float(lat1), float(lon1)], [float(lat2), float(lon2)],
                                     unit='m')  # to get distance in meters

            # If distance is less than 10 km draw the lines
            if distance < circle_radius(val=val["eventType"]) and (val["eventType"] == val2["eventType"]):
                folium.PolyLine(
                    [
                        pd.to_numeric([lat1, lon1]),
                        pd.to_numeric([lat2, lon2])
                    ],
                    color=color_marker(val=val["eventType"]),
                    weight=2,
                    popup='{0:0.3f} km\'s'.format(distance / 1000)
                ).add_to(distance_layer)
                break

    # Add users to map
    ref = db.reference('UserLocation')
    snapshot = ref.get()
    for key, val in snapshot.items():
        folium.Marker(
            val.split(","),
            tooltip=tooltip,
            icon=folium.Icon(color='pink')
        ).add_to(user_location)

    user_location.add_to(m)
    marker_cluster.add_to(m)
    radius_layer.add_to(m)
    distance_layer.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    m.save("maps/index.html")
    return Settings.staticfiles.TemplateResponse("index.html", {"request": request})
