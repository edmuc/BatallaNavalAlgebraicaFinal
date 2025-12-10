#firebase_config.py
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBqGSOJhi_yLoC0TrrIxjnX_jzAtCkh3f0",
    "authDomain": "batalla-naval-fx.firebaseapp.com",
    "databaseURL": "https://batalla-naval-fx-default-rtdb.firebaseio.com/",
    "projectId": "batalla-naval-fx",
    "storageBucket": "batalla-naval-fx.firebasestorage.app",
    "messagingSenderId": "904411896909",
    "appId": "1:904411896909:web:0e33286f11599bab915004",
    "measurementId": "G-ZXR8L53ZRX"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
