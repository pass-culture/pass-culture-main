import requests

identifier= 'Douce-amere'
tcn_request = requests.get('https://www.theatre-contemporain.net/api/spectacles/Douce-amere/?k=2b5b8fde90838e69401fa3ac6c06136b8ae38d0e')
#print(tcn_request.content.decode('utf-8'))
#exit
tcn_info = tcn_request.json
location = []
print(location);
event = []
event['name'] = tcn_info['title']
print(title);
#item = workModel()
#item.identifier = identifier[:20]
#item.name = tcn_info['title']
#import os.path
#thumb_filename = "images_theatre/"+identifier+".jpg"
#if os.path.isfile(thumb_filename):
#with open(thumb_filename, mode='rb') as file:
#    item.thumb = file.read()
#else:
#thumb_request = requests.get(tcn_info['poster'])
#if thumb_request.status_code == 200:
#    item.thumb = thumb_request.content
#Repository.save(item)

#[
#  {
#    "title": "Douce-amère",
#    "object": "Douce-amere",
#    "permanent_url": "https://www.theatre-contemporain.net/spectacles/Douce-amere/",
#         "authors": {
#      "20120": {
#        "lastname": "Poiret",
#        "firstname": "Jean",
#        "object": "Jean-Poiret",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Jean-Poiret/"
#      }
#    },
#    "directors": {
#      "2022": {
#        "lastname": "Fau",
#        "firstname": "Michel",
#        "object": "Michel-Fau",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Michel-Fau/"
#      }
#    },
#    "actors": {
#      "21613": {
#        "lastname": "Doutey",
#        "firstname": "Mélanie",
#        "object": "Melanie-Doutey",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Melanie-Doutey/"
#      },
#      "2022": {
#        "lastname": "Fau",
#        "firstname": "Michel",
#        "object": "Michel-Fau",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Michel-Fau/"
#      },
#      "7076": {
#        "lastname": "Kammenos",
#        "firstname": "David",
#        "object": "KAMMENOS-David",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/KAMMENOS-David/"
#      },
#      "34148": {
#        "lastname": "Laquittant",
#        "firstname": "Rémy",
#        "object": "Remy-Laquittant",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Remy-Laquittant/"
#      },
#      "3080": {
#        "lastname": "Paou",
#        "firstname": "Christophe",
#        "object": "Christophe-Paou",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Christophe-Paou/"
#      }
#    },
#    "distributions": {
#      "13430": {
#        "lastname": "Belugou",
#        "firstname": "David",
#        "roles": {
#          "role_costumes": "Création costumes"
#        },
#        "object": "David-Belugou",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/David-Belugou/"
#      },
#      "40113": {
#        "lastname": "Fabing",
#        "firstname": "Joël",
#        "roles": {
#          "role_lumieres": "Création lumières"
#        },
#        "object": "Joel-Fabing",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Joel-Fabing/"
#      },
#      "28368": {
#        "lastname": "Fau",
#        "firstname": "Bernard",
#        "roles": {
#          "role_decor": "Décors"
#        },
#        "object": "Bernard-Fau",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/Bernard-Fau/"
#      },
#      "11476": {
#        "lastname": "Markoff",
#        "firstname": "Nathacha",
#        "roles": {
#          "role_decor": "Décors"
#        },
#        "object": "MARKOFF-Nathacha",
#        "permanent_url": "https://www.theatre-contemporain.net/biographies/MARKOFF-Nathacha/"
#      }
#    },
#    "poster": "https://www.theatre-contemporain.net/images/upload/spectacles/d/3/round-R7-crop-65x65-22755.jpg",
#    "published": "1",
#    "insert_date": "2018-01-11 14:23:37",
#    "typespectacle": "mise en scène",
#    "near_dates": {
#      "start": "2018-01-24",
#      "end": "2018-04-22",
#      "city": "Paris",
#      "zipcode": "75002",
#      "country": "FR",
#      "place": {
#        "name": "Théâtre des Bouffes parisiens",
#        "object": "THEATRE-DES-BOUFFES-PARISIENS",
#        "permanent_url": "https://www.theatre-contemporain.net/contacts/THEATRE-DES-BOUFFES-PARISIENS/",
#        "geocode": {
#          "x": "0.00000000",
#          "y": "0.00000000"
#        }
#      }
#    }
#  }
#]
