import firebase_admin
from firebase_admin import credentials, db

from config.appConf import logger
from source.models.event.event_controller import find_events


class FirebaseConfig:
    reference = None
    listenerRegistration = None

    def __init__(self):
        cred = credentials.Certificate("account_key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://smartalert-cdd78-default-rtdb.firebaseio.com/',
            'projectId': 'smartalert-cdd78'
        })
        self.reference = db.reference('Events')
        self.listenerRegistration = self.reference.listen(self.userListener)

    def userListener(self, event):
        logger.debug("Listener Started.")
        try:
            logger.debug(event.data)
            # On change in the Events table, recalculate  the events
            find_events(ref=self.reference, master_events_list=None)

        except Exception as e:
            raise Exception("Listener Error " + str(e))

    def stopListening(self):
        logger.debug("Closing Listener")
        self.listenerRegistration.close()
