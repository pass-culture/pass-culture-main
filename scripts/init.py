# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import current_app as app
from pprint import pprint
import traceback

from utils.mock import set_from_mock

@app.manager.command
def init():
    try:
        do_init()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_init():
    check_and_save = app.model.PcObject.check_and_save
    model = app.model

    ## USERS

    # un jeune client qui veut profiter du pass-culture
    client_user = model.User()
    client_user.account = 100
    client_user.email = "arnaud.betremieux@beta.gouv.fr"
    client_user.setPassword("arnaud")
    check_and_save(client_user)
    set_from_mock("thumbs", client_user, 1)

    # un acteur culturel qui peut jouer a rajouter des offres
    # dans un petit libraire (a la mano) - un libraire moyen (via e-paging)
    # un conservatoire (via spreadsheet)
    pro_user = model.User()
    pro_user.email = "erwan.ledoux@beta.gouv.fr"
    pro_user.setPassword("erwan")
    check_and_save(pro_user)
    set_from_mock("thumbs", pro_user, 2)

    # OFFERERS

    # le petit libraire (à la mano)
    offerer = model.Offerer()
    small_library_offerer = offerer
    offerer.name = "MaBoutique"
    offerer.offerProvider = "OpenAgendaOffers"
    offerer.idAtOfferProvider = "80942872"
    check_and_save(offerer)
    set_from_mock("thumbs", offerer, 1)

    userOfferer = model.UserOfferer()
    userOfferer.rights = "admin"
    userOfferer.user = pro_user
    userOfferer.offerer = offerer
    check_and_save(userOfferer)

    # le libraire moyen (via e-paging)
    try:
        offerer = model.Offerer.query\
                               .filter_by(name="Folies d'encre Aulnay-sous-Bois")\
                               .first_or_404()
        userOfferer = model.UserOfferer()
        userOfferer.offerer = offerer
        userOfferer.rights = "admin"
        userOfferer.user = pro_user
        check_and_save(userOfferer)
    except:
        print("WARNING: If you want to bind the pro user to Folies d'encre Aulnay-sous-Bois, You need to do \'pc update_providables -m\'")

    # le conservatoire (via spreadsheet)
    offerer = model.Offerer()
    offerer.name = "l'Avant Seine / théâtre de Colombes"
    offerer.offerProvider = "Spreadsheet"
    offerer.idAtOfferProvider = "avant_seine.xlsx"
    check_and_save(offerer)
    set_from_mock("spreadsheets", offerer, 1)
    set_from_mock("thumbs", offerer, 2)
    set_from_mock("zips", offerer, 1)

    userOfferer = model.UserOfferer()
    userOfferer.rights = "admin"
    userOfferer.user = pro_user
    userOfferer.offerer = offerer
    check_and_save(userOfferer)

    ## VENUES

    venue_bookshop = model.Venue()
    venue_bookshop.name = "MaBoutique"
    venue_bookshop.address = "75 Rue Charles Fourier, 75013 Paris"
    venue_bookshop.latitude = 48.82387
    venue_bookshop.longitude = 2.35284
    check_and_save(venue_bookshop)

    venue_theater = model.Venue()
    venue_theater.name = "Conservatoire National de la Danse"
    venue_theater.address = "209 Avenue Jean Jaurès, 75019 Paris"
    venue_theater.latitude = 48.8889391
    venue_theater.longitude = 2.3887928
    check_and_save(venue_theater)

    ## THINGS

    thing1 = model.Thing()
    thing1.type = model.ThingType.Book
    thing1.description = "Lorsque Jules Verne s’installe en Picardie, il a une quarantaine d’années. Il vient d’acheter son premier bateau, le Saint-Michel, qu’il définit comme sa « maîtresse » et qu’il amarre au Crotoy. Il n’a que deux envies : écrire et naviguer."
    thing1.name = "Jules Verne"
    thing1.type = "Book"
    thing1.identifier = "2912319641"
    thing1.extraData = {
        'author' : "Daniel Compère, Agnès Marcetteau, Piero Gondolo Della Riva",
        'prix_livre' : "12"
    }
    check_and_save(thing1)
    set_from_mock("thumbs", thing1, 1)

    thing2 = model.Thing()
    thing2.type = model.ThingType.Book
    thing2.description = "Accueillir tous les enfants dans la classe ordinaire, considérer avant tout ce qui les rassemble plutôt que ce qui les distingue… voilà ce que met de l’avant cet ouvrage qui vise à contribuer à l’émergence d’une pratique pédagogique inclusive responsable en s’appuyant sur ce qu’elle est fondamentalement et sur les changements organisationnels et pédagogiques qu’elle sous-tend. Entièrement réorganisée et comportant de nouveaux chapitres, cette troisième édition reflète les progrès de la recherche en matière d’inclusion scolaire et répond aux préoccupations grandissantes du personnel enseignant relativement à la pratique de l’inclusion scolaire. Réunissant les textes d’une trentaine de chercheurs, elle permet de développer une meilleure compréhension de ce qu’est l’inclusion scolaire et de découvrir des dimensions planificatrices et créatrices liées à toute pratique pédagogique destinée à une diversité d’élèves. Elle comprend également un glossaire des concepts clés facilitant l’utilisation d’un langage commun chez l’ensemble des acteurs de la pédagogie inclusive. Essentiel à la formation initiale et continue en éducation, cet ouvrage montre que l’éducation inclusive est certes un projet ambitieux, mais combien stimulant, et ce, tant pour les acteurs de l’éducation qui se l’approprient que pour l’ensemble des membres de la communauté qui en bénéficient."
    thing2.name = "La pédagogie de l'inclusion scolaire"
    thing2.type = "Book"
    thing2.identifier = "276051272X"
    thing2.extraData = {
        'author' : "Nadia Rousseau, Stéphanie Bélanger",
        'prix_livre' : "10"
    }
    check_and_save(thing2)
    set_from_mock("thumbs", thing2, 2)

    thing3 = model.Thing()
    thing3.type = model.ThingType.Book
    thing3.description = "Un des grands mérites de cet ouvrage, désormais classique, est d’avoir montré comment la doctrine politique de Rousseau résultait concrètement d’une réflexion approfondie sur les théories soutenues par l’Ecole du droit de la nature et des gens. C’est cette situtation de Rousseau dans la science politique de son temps qui permet à la fois d’apprécier son génie propre et de mesurer exactement son originalité. Le problème historique des sources de la pensée politique de Rousseau est certes difficile, mais son enjeu est tout à fait capital : en raison même des multiples allusions qu’il renferme, et dont le sens échappe au lecteur actuel, le Contrat Social notamment reste l’un des textes les plus obscurs de la littérature politique. C’est donc avant tout pour dégager ce que Rousseau doit à ses prédécesseurs et ce qu’il apporte de radicalement nouveau que R. Derathé a mené cette large enquête qui fait toujours autorité."
    thing3.name = "Jean-Jacques Rousseau et la science politique de son temps"
    thing3.type = "Book"
    thing3.identifier = "2711601781"
    thing3.extraData = {
        'author' : "Robert Derathé",
        'prix_livre' : "13.3"
    }
    thing3.thumbCount = 1
    check_and_save(thing3)
    set_from_mock("thumbs", thing3, 3)

    thing4 = model.Thing()
    thing4.type = model.ThingType.Book
    thing4.description = "Roman d'aventures, écrit par Jules Verne, publié en 1872. Il raconte la course autour du monde d'un gentleman anglais, Phileas Fogg, qui a fait le pari d'y parvenir en 80 jours. Il est accompagné par Jean Passepartout, son serviteur français. L'ensemble du roman est un habile mélange entre récit de voyage (traditionnel pour Jules Verne) et données scientifiques comme celle utilisée pour le rebondissement de la chute du roman."
    thing4.name = "Le Tour du monde en 80 jours (édition enrichie illustrée)"
    thing4.type = "Book"
    thing4.identifier = "2072534054"
    thing4.extraData = {
        'author' : "Jules Verne",
        'prix_livre' : "13.99"
    }
    thing4.thumbCount = 1
    check_and_save(thing4)
    set_from_mock("thumbs", thing4, 4)

    ## OFFERS

    # offer 1 without user mediation
    offer = model.Offer()
    offer.offerer = small_library_offerer
    offer.thing = thing1
    offer.price = 7
    offer.venue = venue_bookshop
    check_and_save(offer)

    # offer 2 with automatic user mediation
    offer = model.Offer()
    offer.offerer = small_library_offerer
    offer.price = 10
    offer.venue = venue_bookshop
    offer.thing = thing2
    check_and_save(offer)
    user_mediation = model.UserMediation()
    first_user_mediation = model.UserMediation.query\
                                              .filter_by(user=client_user)\
                                              .first()
    user_mediation.user = client_user
    user_mediation.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(user_mediation)
    if first_user_mediation is None:
        user_mediation.isFirst = True
        umo = model.UserMediationOffer()
        umo.offer = offer
        umo.userMediation = user_mediation
        check_and_save(umo)

    # offer 3
    offer = model.Offer()
    offer.offerer = small_library_offerer
    offer.venue = venue_bookshop
    offer.thing = thing3
    offer.price = 15
    check_and_save(offer)
    user_mediation = model.UserMediation()
    user_mediation.isFavorite = True
    mediation = model.Mediation()
    mediation.author = pro_user
    mediation.text = "Pour se réconcilier une bonne fois pour toute avec Jean-Jacques"
    mediation.thing = thing3
    check_and_save(mediation)
    user_mediation.mediation = mediation
    user_mediation.user = client_user
    user_mediation.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(user_mediation)
    umo = model.UserMediationOffer()
    umo.offer = offer
    umo.userMediation = user_mediation
    check_and_save(umo)

    # offer 4
    offer = model.Offer()
    offer.offerer = small_library_offerer
    offer.price = 8
    offer.venue = venue_bookshop
    offer.thing = thing4
    check_and_save(offer)
    user_mediation = model.UserMediation()
    mediation = model.Mediation()
    mediation.author = pro_user
    mediation.text = "Histoire de voyager sans augmenter son bilan carbone"
    mediation.thing = thing4
    user_mediation.mediation = mediation
    user_mediation.user = client_user
    user_mediation.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(user_mediation)
    umo = model.UserMediationOffer()
    umo.offer = offer
    umo.userMediation = user_mediation
    check_and_save(umo)
