from models import PcObject
from repository.offer_queries import get_offers_for_recommendations_search

from tests.conftest import clean_database

from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_product_with_event_type, \
    create_offer_with_event_product, create_event_occurrence


@clean_database
def test_get_offers_for_recommendations_search_with_distance_less_than_1km_returns_one_offer_in_venue_with_coordonnates_that_match(
        app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue77 = create_venue(
        offerer75,
        name='Centre Culturel Municipal Jacques Prévert',
        city="Villeparisis",
        departement_code='77',
        is_virtual=False,
        longitude="2.614391",
        latitude="48.942623",
        siret="50763357600077"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue92 = create_venue(
        offerer75,
        name='2G – Théâtre de Gennevilliers',
        city="Gennevilliers",
        departement_code='92',
        is_virtual=False,
        longitude="2.2985554",
        latitude="48.9143444",
        siret="50763357600092"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')

    concert_offer75 = create_offer_with_event_product(venue75, concert_event)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer77 = create_offer_with_event_product(venue77, concert_event)
    concert_offer92 = create_offer_with_event_product(venue92, concert_event)

    concert_event_occurrence75 = create_event_occurrence(concert_offer75)
    concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

    concert_event_occurrence77 = create_event_occurrence(concert_offer77)
    concert_stock77 = create_stock_from_event_occurrence(concert_event_occurrence77)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence92 = create_event_occurrence(concert_offer92)
    concert_stock92 = create_stock_from_event_occurrence(concert_event_occurrence92)

    PcObject.save(concert_stock75, concert_stock77, concert_stock78, concert_stock92)

    # When
    # User in Mantes-la-jolie
    offers = get_offers_for_recommendations_search(max_distance=1, longitude=2.713513, latitude=48.985968)

    # Then
    assert concert_offer75 not in offers
    assert concert_offer77 not in offers
    assert concert_offer78 in offers
    assert concert_offer92 not in offers


@clean_database
def test_get_offers_for_recommendations_search_with_all_distances_should_returns_all_offers(app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue13 = create_venue(
        offerer75,
        name='Friche La Belle de Mai',
        city="Marseille",
        departement_code='13',
        is_virtual=False,
        longitude="5.3764073",
        latitude="43.303906",
        siret="50763357600013"
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue92 = create_venue(
        offerer75,
        name='2G – Théâtre de Gennevilliers',
        city="Gennevilliers",
        departement_code='92',
        is_virtual=False,
        longitude="2.2985554",
        latitude="48.9143444",
        siret="50763357600092"
    )
    venue77 = create_venue(
        offerer75,
        name='Centre Culturel Municipal Jacques Prévert',
        city="Villeparisis",
        departement_code='77',
        is_virtual=False,
        longitude="2.614391",
        latitude="48.942623",
        siret="50763357600077"
    )
    venue91 = create_venue(
        offerer75,
        name='Théâtre de Longjumeau',
        city="Longjumeau",
        departement_code='91',
        is_virtual=False,
        longitude="2.2881266",
        latitude="48.6922895",
        siret="50763357600091"
    )
    venue93 = create_venue(
        offerer75,
        name='La Salle',
        city="Aulnay Sous Bois",
        departement_code='93',
        is_virtual=False,
        longitude="2.3458074",
        latitude="48.9247067",
        siret="50763357600093"
    )
    venue94 = create_venue(
        offerer75,
        name='Centre Culturel Municipal Jacques Prévert',
        city="Cachan",
        departement_code='91',
        is_virtual=False,
        longitude="2.3231582",
        latitude="48.7914281",
        siret="50763357600094"
    )
    venue95 = create_venue(
        offerer75,
        name='EMB',
        city="Sannois",
        departement_code='95',
        is_virtual=False,
        longitude="2.2683263",
        latitude="48.976826",
        siret="50763357600095"
    )
    venue973 = create_venue(
        offerer75,
        name='Théâtre de Macouria',
        city="Cayenne",
        departement_code='973',
        is_virtual=False,
        longitude="-52.423277",
        latitude="4.9780178",
        siret="50763357600973"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')

    concert_offer13 = create_offer_with_event_product(venue13, concert_event)
    concert_offer75 = create_offer_with_event_product(venue75, concert_event)
    concert_offer77 = create_offer_with_event_product(venue77, concert_event)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer91 = create_offer_with_event_product(venue91, concert_event)
    concert_offer92 = create_offer_with_event_product(venue92, concert_event)
    concert_offer93 = create_offer_with_event_product(venue93, concert_event)
    concert_offer94 = create_offer_with_event_product(venue94, concert_event)
    concert_offer95 = create_offer_with_event_product(venue95, concert_event)
    concert_offer973 = create_offer_with_event_product(venue973, concert_event)

    concert_event_occurrence13 = create_event_occurrence(concert_offer13)
    concert_stock13 = create_stock_from_event_occurrence(concert_event_occurrence13)

    concert_event_occurrence91 = create_event_occurrence(concert_offer91)
    concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

    concert_event_occurrence93 = create_event_occurrence(concert_offer93)
    concert_stock93 = create_stock_from_event_occurrence(concert_event_occurrence93)

    concert_event_occurrence94 = create_event_occurrence(concert_offer94)
    concert_stock94 = create_stock_from_event_occurrence(concert_event_occurrence94)

    concert_event_occurrence95 = create_event_occurrence(concert_offer95)
    concert_stock95 = create_stock_from_event_occurrence(concert_event_occurrence95)

    concert_event_occurrence973 = create_event_occurrence(concert_offer973)
    concert_stock973 = create_stock_from_event_occurrence(concert_event_occurrence973)

    PcObject.save(concert_stock13, concert_stock95, concert_stock91, concert_stock93, concert_stock94, concert_stock973)

    # When
    # User in Mantes-la-jolie
    offers = get_offers_for_recommendations_search(max_distance=20000, longitude=2.713513, latitude=48.985968)

    # Then
    assert concert_offer13 in offers
    assert concert_offer91 in offers
    assert concert_offer93 in offers
    assert concert_offer94 in offers
    assert concert_offer95 in offers
    assert concert_offer973 in offers


@clean_database
def test_get_offers_for_recommendations_search_with_distance_less_than_20kms_returns_one_offer_in_venue_with_coordonnates_that_match_with_user_in_Paris(
        app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue77 = create_venue(
        offerer75,
        name='Centre Culturel Municipal Jacques Prévert',
        city="Villeparisis",
        departement_code='77',
        is_virtual=False,
        longitude="2.614391",
        latitude="48.942623",
        siret="50763357600077"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue91 = create_venue(
        offerer75,
        name='Théâtre de Orsay',
        city="Orsay",
        departement_code='91',
        is_virtual=False,
        longitude="2.1911928",
        latitude="48.7034926",
        siret="50763357600091"
    )
    venue92 = create_venue(
        offerer75,
        name='2G – Théâtre de Gennevilliers',
        city="Gennevilliers",
        departement_code='92',
        is_virtual=False,
        longitude="2.2985554",
        latitude="48.9143444",
        siret="50763357600092"
    )
    venue93 = create_venue(
        offerer75,
        name='La Salle',
        city="Aulnay Sous Bois",
        departement_code='93',
        is_virtual=False,
        longitude="2.3458074",
        latitude="48.9247067",
        siret="50763357600093"
    )
    venue95 = create_venue(
        offerer75,
        name='EMB',
        city="Sannois",
        departement_code='95',
        is_virtual=False,
        longitude="2.2683263",
        latitude="48.976826",
        siret="50763357600095"
    )
    venue94 = create_venue(
        offerer75,
        name='Centre Culturel Municipal Jacques Prévert',
        city="Cachan",
        departement_code='91',
        is_virtual=False,
        longitude="2.3231582",
        latitude="48.7914281",
        siret="50763357600094"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')

    concert_offer75 = create_offer_with_event_product(venue75, concert_event)
    concert_offer77 = create_offer_with_event_product(venue77, concert_event)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer91 = create_offer_with_event_product(venue91, concert_event)
    concert_offer92 = create_offer_with_event_product(venue92, concert_event)
    concert_offer93 = create_offer_with_event_product(venue93, concert_event)
    concert_offer94 = create_offer_with_event_product(venue94, concert_event)
    concert_offer95 = create_offer_with_event_product(venue95, concert_event)

    concert_event_occurrence75 = create_event_occurrence(concert_offer75)
    concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

    concert_event_occurrence77 = create_event_occurrence(concert_offer77)
    concert_stock77 = create_stock_from_event_occurrence(concert_event_occurrence77)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence91 = create_event_occurrence(concert_offer91)
    concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

    concert_event_occurrence92 = create_event_occurrence(concert_offer92)
    concert_stock92 = create_stock_from_event_occurrence(concert_event_occurrence92)

    concert_event_occurrence93 = create_event_occurrence(concert_offer93)
    concert_stock93 = create_stock_from_event_occurrence(concert_event_occurrence93)

    concert_event_occurrence94 = create_event_occurrence(concert_offer94)
    concert_stock94 = create_stock_from_event_occurrence(concert_event_occurrence94)

    concert_event_occurrence95 = create_event_occurrence(concert_offer95)
    concert_stock95 = create_stock_from_event_occurrence(concert_event_occurrence95)

    PcObject.save(concert_stock75, concert_stock77, concert_stock78, concert_stock91, concert_stock92, concert_stock93,
                  concert_stock94, concert_stock95)

    # When
    # User in Paris
    offers = get_offers_for_recommendations_search(max_distance=20, longitude=2.4002701, latitude=48.8363788)

    # Then
    assert concert_offer75 in offers
    assert concert_offer77 in offers
    assert concert_offer78 not in offers
    assert concert_offer91 not in offers
    assert concert_offer92 in offers
    assert concert_offer93 in offers
    assert concert_offer94 in offers
    assert concert_offer95 in offers


@clean_database
def test_get_offers_for_recommendations_search_with_distance_less_than_50kms_returns_one_offer_in_venue_with_coordonnates_that_match_with_user_in_Paris(
        app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue45 = create_venue(
        offerer75,
        name='Salle Albert Camus',
        city="Orléans",
        departement_code='45',
        is_virtual=False,
        longitude="1.9201176",
        latitude="47.9063667",
        siret="50763357600045"
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue91 = create_venue(
        offerer75,
        name='Théâtre de Orsay',
        city="Orsay",
        departement_code='91',
        is_virtual=False,
        longitude="2.1911928",
        latitude="48.7034926",
        siret="50763357600091"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')

    concert_offer45 = create_offer_with_event_product(venue45, concert_event)
    concert_offer75 = create_offer_with_event_product(venue75, concert_event)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer91 = create_offer_with_event_product(venue91, concert_event)

    concert_event_occurrence45 = create_event_occurrence(concert_offer45)
    concert_stock45 = create_stock_from_event_occurrence(concert_event_occurrence45)

    concert_event_occurrence75 = create_event_occurrence(concert_offer75)
    concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence91 = create_event_occurrence(concert_offer91)
    concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

    PcObject.save(concert_stock45, concert_stock75, concert_stock78, concert_offer91)

    # When
    # User in Paris
    offers = get_offers_for_recommendations_search(max_distance=50, longitude=2.4002701, latitude=48.8363788)

    # Then
    assert concert_offer45 not in offers
    assert concert_offer75 in offers
    assert concert_offer78 in offers
    assert concert_offer91 in offers


@clean_database
def test_get_offers_for_recommendations_search_with_distance_returns_offers_in_virtuals_venues_no_matter_wich_distance_with_user_in_Paris(
        app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue45 = create_venue(
        offerer75,
        name='Salle Albert Camus',
        city="Orléans",
        departement_code='45',
        is_virtual=True,
        longitude="1.9201176",
        latitude="47.9063667",
        siret=None
    )
    venue13 = create_venue(
        offerer75,
        name='Friche La Belle de Mai',
        city="Marseille",
        departement_code='13',
        is_virtual=True,
        longitude="5.3764073",
        latitude="43.303906",
        siret=None
    )
    venue973 = create_venue(
        offerer75,
        name='Théâtre de Macouria',
        city="Cayenne",
        departement_code='973',
        is_virtual=True,
        longitude="-52.423277",
        latitude="4.9780178",
        siret=None
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')

    concert_offer13 = create_offer_with_event_product(venue13, concert_event)
    concert_offer45 = create_offer_with_event_product(venue45, concert_event)
    concert_offer973 = create_offer_with_event_product(venue973, concert_event)

    concert_event_occurrence13 = create_event_occurrence(concert_offer13)
    concert_stock13 = create_stock_from_event_occurrence(concert_event_occurrence13)

    concert_event_occurrence45 = create_event_occurrence(concert_offer45)
    concert_stock45 = create_stock_from_event_occurrence(concert_event_occurrence45)

    concert_event_occurrence973 = create_event_occurrence(concert_offer973)
    concert_stock973 = create_stock_from_event_occurrence(concert_event_occurrence973)

    PcObject.save(concert_stock13, concert_stock45, concert_stock973)

    # When
    # User in Paris
    offers = get_offers_for_recommendations_search(max_distance=1, longitude=2.4002701, latitude=48.8363788)

    # Then
    assert concert_offer45 not in offers
    assert concert_offer13 not in offers
    assert concert_offer973 not in offers


@clean_database
def test_get_offers_for_recommendations_search_with_specific_distance_and_keywords(app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue45 = create_venue(
        offerer75,
        name='Salle Albert Camus',
        city="Orléans",
        departement_code='45',
        is_virtual=False,
        longitude="1.9201176",
        latitude="47.9063667",
        siret="50763357600045"
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue91 = create_venue(
        offerer75,
        name='Théâtre de Orsay',
        city="Orsay",
        departement_code='91',
        is_virtual=False,
        longitude="2.1911928",
        latitude="48.7034926",
        siret="50763357600091"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')
    concert_event2 = create_product_with_event_type('Kiwi')

    concert_offer45 = create_offer_with_event_product(venue45, concert_event)
    kiwi_concert_offer75 = create_offer_with_event_product(venue75, concert_event2)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer91 = create_offer_with_event_product(venue91, concert_event)

    concert_event_occurrence45 = create_event_occurrence(concert_offer45)
    concert_stock45 = create_stock_from_event_occurrence(concert_event_occurrence45)

    kiwi_concert_event_occurrence75 = create_event_occurrence(kiwi_concert_offer75)
    kiwi_concert_stock75 = create_stock_from_event_occurrence(kiwi_concert_event_occurrence75)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence91 = create_event_occurrence(concert_offer91)
    concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

    PcObject.save(concert_stock45, kiwi_concert_stock75, concert_stock78, concert_offer91)

    # When
    # User in Paris
    offers = get_offers_for_recommendations_search(max_distance=1, longitude=2.4002701, latitude=48.8363788,
                                                   keywords_string='Kiwi')

    # Then
    assert concert_offer45 not in offers
    assert kiwi_concert_offer75 in offers
    assert concert_offer78 not in offers
    assert concert_offer91 not in offers


@clean_database
def test_get_offers_for_recommendations_search_with_all_distance_and_keywords(app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
    )
    venue45 = create_venue(
        offerer75,
        name='Salle Albert Camus',
        city="Orléans",
        departement_code='45',
        is_virtual=False,
        longitude="1.9201176",
        latitude="47.9063667",
        siret="50763357600045"
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue91 = create_venue(
        offerer75,
        name='Théâtre de Orsay',
        city="Orsay",
        departement_code='91',
        is_virtual=False,
        longitude="2.1911928",
        latitude="48.7034926",
        siret="50763357600091"
    )

    concert_event = create_product_with_event_type('Concert de Gael Faye')
    concert_event2 = create_product_with_event_type('Kiwi')

    concert_offer45 = create_offer_with_event_product(venue45, concert_event)
    kiwi_concert_offer75 = create_offer_with_event_product(venue75, concert_event2)
    concert_offer78 = create_offer_with_event_product(venue78, concert_event)
    concert_offer91 = create_offer_with_event_product(venue91, concert_event)

    concert_event_occurrence45 = create_event_occurrence(concert_offer45)
    concert_stock45 = create_stock_from_event_occurrence(concert_event_occurrence45)

    kiwi_concert_event_occurrence75 = create_event_occurrence(kiwi_concert_offer75)
    kiwi_concert_stock75 = create_stock_from_event_occurrence(kiwi_concert_event_occurrence75)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence91 = create_event_occurrence(concert_offer91)
    concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

    PcObject.save(concert_stock45, kiwi_concert_stock75, concert_stock78, concert_offer91)

    # When
    # User in Paris
    offers = get_offers_for_recommendations_search(max_distance=20000, longitude=2.4002701, latitude=48.8363788,
                                                   keywords_string='Kiwi')

    # Then
    assert concert_offer45 not in offers
    assert kiwi_concert_offer75 in offers
    assert concert_offer78 not in offers
    assert concert_offer91 not in offers
