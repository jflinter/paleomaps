from pymongo import Connection, GEO2D

db = Connection().paleo_database
db.paleo_webapp_place.create_index([("latlng", GEO2D)])