""" init script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pprint import pprint
import traceback
from flask import current_app as app

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
    client_user.publicName = "Arnaud Bétrémieux"
    client_user.account = 100
    client_user.email = "arnaud.betremieux@beta.gouv.fr"
    client_user.setPassword("arnaud123")
    check_and_save(client_user)
    #set_from_mock("thumbs", client_user, 1)
    client_user.save_thumb('https://avatars3.githubusercontent.com/u/185428?s=400&v=4', 0)

    # un acteur culturel qui peut jouer a rajouter des offres
    # dans un petit libraire (a la mano) - un libraire moyen (via e-paging)
    # un conservatoire (via spreadsheet)
    pro_user = model.User()
    pro_user.publicName = "Erwan Ledoux"
    pro_user.email = "erwan.ledoux@beta.gouv.fr"
    pro_user.setPassword("erwan123")
    check_and_save(pro_user)
    set_from_mock("thumbs", pro_user, 2)

    # OFFERERS

    # le petit libraire (à la mano)
    offerer = model.Offerer()
    small_library_offerer = offerer
    offerer.name = "MaBoutique"
    offerer.bookingEmail = "passculture-dev@beta.gouv.fr"
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
    offerer.bookingEmail = "passculture-dev@beta.gouv.fr"
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

    venue_museum = model.Venue()
    venue_museum.name = "Musée d'Orsay"
    venue_museum.address = "1 rue de la Légion d'Honneur, 75007 Paris"
    venue_museum.latitude = 48.8599614
    venue_museum.longitude = 2.3243727
    check_and_save(venue_museum)

    venue_mc = model.Venue()
    venue_mc.name = "Maison de la Culture de la Seine Saint-Denis"
    venue_mc.address = "9 boulevard Lénine, 93000 Bobigny"
    venue_mc.latitude = 48.9066951
    venue_mc.longitude = 2.4400193
    check_and_save(venue_museum)


    ## THING 1 WITH THUMB MEDIATION

    thing1 = model.Thing()
    thing1.description = "Howard Phillips Lovecraft est sans nul doute l'auteur fantastique le plus influent du xxe siècle. Son imaginaire unique et terrifiant n'a cessé d'inspirer des générationsd'écrivains, de cinéastes, d'artistes ou de créateurs d'univers de jeux, de Neil Gaiman à Michel Houellebecq en passant par Metallica. Le mythe de Cthulhu est au coeur de cette oeuvre : un panthéon de dieux et d'êtres monstrueux venus du cosmos et de la nuit des temps ressurgissent pour reprendre possession de notre monde. Ceux qui en sont témoins sont voués à la folie et à la destruction. Les neuf récits essentiels du mythe sont ici réunis dans une toute nouvelle traduction. À votre tour, vous allez pousser la porte de la vieille bâtisse hantée qu'est la Maison de la Sorcière, rejoindre un mystérieux festival où l'on célèbre un rite impie, découvrir une cité antique enfouie sous le sable, ou échouer dans une ville portuaire dépeuplée dont les derniers habitants sont atrocement déformés.."
    thing1.name = "Cthulhu ; le mythe"
    thing1.type = model.ThingType.Book
    thing1.identifier = "9782352945536"
    thing1.extraData = {
        'author' : "Howard Phillips Lovecraft",
        'prix_livre' : "25"
    }
    check_and_save(thing1)
    set_from_mock("thumbs", thing1, 1)

    offer1 = model.Offer()
    offer1.offerer = small_library_offerer
    offer1.thing = thing1
    offer1.price = 25
    offer1.available = 2
    offer1.venue = venue_bookshop
    check_and_save(offer1)

    mediation1 = model.Mediation()
    mediation1.author = pro_user
    mediation1.backText = "Cthulhu le Mythe, livre I, de H.P. Lovecraft, pour un premier pas dans la littérature… frissons garantis ! Howard Phillips Lovecraft, né le 20 août 1890 à Providence (Rhode Island) et mort le 15 mars 1937 dans la même ville, est un écrivain américain connu pour ses récits fantastiques, d'horreur et de science-fiction."
    mediation1.thing = thing1
    mediation1.what = "Un des trois tomes de Cthulhu le Mythe, au choix"
    check_and_save(mediation1)
    set_from_mock("thumbs", mediation1, 1)

    """
    recommendation1 = model.Recommendation()
    first_recommendation = model.Recommendation.query\
                           .filter_by(user=client_user)\
                           .first()
    if first_recommendation is None:
        recommendation1.isFirst = True
    recommendation1.user = client_user
    recommendation1.validUntilDate = datetime.now() + timedelta(days=2)
    recommendation1.mediation = mediation1
    check_and_save(recommendation1)

    recommendation_offer1 = model.RecommendationOffer()
    recommendation_offer1.offer = offer1
    recommendation_offer1.Recommendation = recommendation1
    check_and_save(recommendation_offer1)

    booking1 = model.Booking()
    booking1.user = client_user
    booking1.offer = offer1
    booking1.token = 'FUUEEM'
    booking1.Recommendation = recommendation1
    check_and_save(booking1)

    umb1 = model.RecommendationBooking()
    umb1.booking = booking1
    umb1.Recommendation = recommendation1
    check_and_save(umb1)
    """

    ## EVENT 2 WITHOUT MEDIATION

    event2 = model.Event()
    event2.isActive = True
    event2.dateModifiedAtLastProvider = '2018-03-05T13:00:00'
    event2.description = "Atelier d'initiation avec la création d'une page (4 à 6 cases) sur un scénario collectif ou un scénario individuel imaginé par les participants.\n Le créateur du Chat du Rabbin et de Petit Vampire vous attend dans la Maison de la Culture du 93 pour un atelier bande dessinée suivi d’une séance de dédicace."
    event2.durationMinutes = 150
    event2.name = "Atelier BD et dédicace avec Joann Sfar à la MC93"
    event2.type = model.EventType.LiteraryEvent
    check_and_save(event2)
    set_from_mock("thumbs", event2, 1)

    eventOccurence2 = model.EventOccurence()
    eventOccurence2.beginningDatetime = '2018-03-05T14:30:00'
    eventOccurence2.event = event2
    eventOccurence2.venue = venue_mc
    check_and_save(eventOccurence2)

    offer2 = model.Offer()
    offer2.offerer = small_library_offerer
    offer2.eventOccurence = eventOccurence2
    offer2.price = 10
    check_and_save(offer2)

    """
    recommendation2 = model.Recommendation()
    recommendation2.user = client_user
    recommendation2.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(recommendation2)

    recommendation_offer2 = app.model.RecommendationOffer()
    recommendation_offer2.offer = offer2
    recommendation_offer2.Recommendation = recommendation2
    check_and_save(recommendation_offer2)
    """

    ## EVENT 3 WITH THUMB MEDIATION

    event3 = model.Event()
    event3.description = "Visite guidée de 1h30 du musée pour des groupes de minimum 15 personnes."
    event3.durationMinutes = 60
    event3.isActive = True
    event3.name = "Visite Nocturne"
    event3.type = model.EventType.VisualArtsEvent
    check_and_save(event3)
    set_from_mock("thumbs", event3, 3)

    eventOccurence3 = model.EventOccurence()
    eventOccurence3.beginningDatetime = '2018-03-05T22:00:00'
    eventOccurence3.event = event3
    eventOccurence3.venue = venue_museum
    check_and_save(eventOccurence3)

    offer3 = model.Offer()
    offer3.offerer = small_library_offerer
    offer3.eventOccurence = eventOccurence3
    offer3.price = 8
    check_and_save(offer3)

    mediation3 = model.Mediation()
    mediation3.author = pro_user
    mediation3.backText = "En compagnie d’un accompagnateur, découvrez les dessous d’Orsay lors d’une séance nocturne de 1h30 où le musée est à vous. D’où viennent donc ces dinosaures dans L'angélus de Millet ?"
    mediation3.event = event3
    mediation3.what = "Atelier d'initiation avec la création d'une page (4 à 6 cases) sur un scénario collectif ou un scénario individuel imaginé par les participants."
    check_and_save(mediation3)
    set_from_mock("thumbs", mediation3, 2)

    """
    recommendation3 = model.Recommendation()
    recommendation3.mediation = mediation3
    recommendation3.user = client_user
    recommendation3.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(recommendation3)
    recommendation_offer3 = model.RecommendationOffer()
    recommendation_offer3.offer = offer3
    recommendation_offer3.Recommendation = recommendation3
    check_and_save(recommendation_offer3)
    """

    ## THING 4 WITH TEXT MEDIATION

    thing4 = model.Thing()
    thing4.description = "Roman d'aventures, écrit par Jules Verne, publié en 1872. Il raconte la course autour du monde d'un gentleman anglais, Phileas Fogg, qui a fait le pari d'y parvenir en 80 jours. Il est accompagné par Jean Passepartout, son serviteur français. L'ensemble du roman est un habile mélange entre récit de voyage (traditionnel pour Jules Verne) et données scientifiques comme celle utilisée pour le rebondissement de la chute du roman."
    thing4.extraData = {
        'author' : "Jules Verne",
        'prix_livre' : "13.99"
    }
    thing4.identifier = "2072534054"
    thing4.name = "Le Tour du monde en 80 jours (édition enrichie illustrée)"
    thing4.type = model.ThingType.Book
    check_and_save(thing4)
    set_from_mock("thumbs", thing4, 4)

    offer4 = model.Offer()
    offer4.offerer = small_library_offerer
    offer4.price = 8
    offer4.venue = venue_bookshop
    offer4.thing = thing4
    check_and_save(offer4)

    mediation4 = model.Mediation()
    mediation4.author = pro_user
    mediation4.backText = "Jules Verne savait-il déjà que le voyage en ballon serait le transport du futur ?"
    mediation4.frontText = "Comment voyager sans augmenter son bilan carbone ?"
    mediation4.thing = thing4

    """
    recommendation4 = model.Recommendation()
    recommendation4.mediation = mediation4
    recommendation4.user = client_user
    recommendation4.validUntilDate = datetime.now() + timedelta(days=2)
    check_and_save(recommendation4)

    recommendation_offer4 = model.RecommendationOffer()
    recommendation_offer4.offer = offer4
    recommendation_offer4.Recommendation = recommendation4
    check_and_save(recommendation_offer4)
    """
