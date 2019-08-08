def remove_ids(response) -> dict:
    if isinstance(response, list):
        for data in response:
            _remove_ids_in_dict(data)
    if isinstance(response, dict):
        _remove_ids_in_dict(response)


def _remove_ids_in_dict(data):
    for k, v in data.items():
        if k.endswith('Id') or k == 'id':
            data[k] = 'someId'
        if isinstance(v, dict):
            remove_ids(v)
        if isinstance(v, list):
            for c in v:
                remove_ids(c)


JSON_OUTPUT = [{'amount': 22950.0,
                'dateCreated': '2019-08-08T08:03:14.322540Z',
                'id': 'BE',
                'isCancelled': False,
                'isUsed': False,
                'modelName': 'Booking',
                'quantity': 1,
                'recommendationId': 'BE',
                'reimbursed_amount': 0.0,
                'reimbursement_rule': 'Pas de remboursement au dessus du plafond de 20 000 € '
                                      'par offreur',
                'stock': {'available': 50,
                          'beginningDatetime': None,
                          'bookingLimitDatetime': None,
                          'bookingRecapSent': None,
                          'dateModified': '2019-08-08T08:03:14.792272Z',
                          'dateModifiedAtLastProvider': '2019-08-08T08:03:14.792268Z',
                          'endDatetime': None,
                          'groupSize': 1,
                          'id': 'BE',
                          'idAtProviders': None,
                          'isSoftDeleted': False,
                          'lastProviderId': None,
                          'modelName': 'Stock',
                          'offerId': 'BE',
                          'price': 22950.0,
                          'resolvedOffer': {'ageMax': None,
                                            'ageMin': None,
                                            'baseScore': 0,
                                            'bookingEmail': 'offer.booking.email@test.com',
                                            'conditions': None,
                                            'dateCreated': '2019-08-08T08:03:14.322574Z',
                                            'dateModifiedAtLastProvider': '2019-08-08T08:03:14.782853Z',
                                            'description': None,
                                            'durationMinutes': None,
                                            'extraData': {'author': 'Test Author'},
                                            'id': 'BE',
                                            'idAtProviders': '2032939005261@12345678912345',
                                            'isActive': True,
                                            'isFinished': False,
                                            'isFullyBooked': False,
                                            'isNational': False,
                                            'lastProviderId': None,
                                            'mediaUrls': ['test/urls'],
                                            'modelName': 'Offer',
                                            'name': 'Test Book',
                                            'product': {'ageMax': None,
                                                        'ageMin': None,
                                                        'conditions': None,
                                                        'dateModifiedAtLastProvider': '2019-08-08T08:03:14.776808Z',
                                                        'description': None,
                                                        'durationMinutes': None,
                                                        'extraData': {'author': 'Test '
                                                                                'Author'},
                                                        'firstThumbDominantColor': [0, 0, 0],
                                                        'id': 'BE',
                                                        'idAtProviders': '2032939005261',
                                                        'isNational': False,
                                                        'lastProviderId': None,
                                                        'mediaUrls': ['test/urls'],
                                                        'modelName': 'Product',
                                                        'name': 'Test Book',
                                                        'offerType': {'appLabel': 'Films sur '
                                                                                  'supports '
                                                                                  'physiques '
                                                                                  'et VOD',
                                                                      'conditionalFields': [],
                                                                      'description': 'Action, '
                                                                                     'science-fiction, '
                                                                                     'documentaire '
                                                                                     'ou '
                                                                                     'comédie '
                                                                                     'sentimentale '
                                                                                     '? En '
                                                                                     'salle, '
                                                                                     'en '
                                                                                     'plein '
                                                                                     'air ou '
                                                                                     'bien '
                                                                                     'au '
                                                                                     'chaud '
                                                                                     'chez '
                                                                                     'soi ? '
                                                                                     'Et si '
                                                                                     'c’était '
                                                                                     'plutôt '
                                                                                     'cette '
                                                                                     'exposition '
                                                                                     'qui '
                                                                                     'allait '
                                                                                     'faire '
                                                                                     'son '
                                                                                     'cinéma '
                                                                                     '?',
                                                                      'offlineOnly': False,
                                                                      'onlineOnly': False,
                                                                      'proLabel': 'Audiovisuel '
                                                                                  '— films '
                                                                                  'sur '
                                                                                  'supports '
                                                                                  'physiques '
                                                                                  'et VOD',
                                                                      'sublabel': 'Regarder',
                                                                      'type': 'Thing',
                                                                      'value': 'ThingType.AUDIOVISUEL'},
                                                        'owningOffererId': None,
                                                        'thumbCount': 1,
                                                        'thumbUrl': 'https://storage.gra3.cloud.ovh.net/v1/AUTH_688df1e25bd84a48a3804e7fa8938085/storage-pc-dev/thumbs/products/BE',
                                                        'type': 'ThingType.AUDIOVISUEL',
                                                        'url': None},
                                            'productId': 'BE',
                                            'type': 'ThingType.AUDIOVISUEL',
                                            'url': None,
                                            'venueId': 'AM'}},
                'stockId': 'BE',
                'token': None,
                'user': {'email': 'test@email.com', 'firstName': 'John', 'lastName': 'Doe'},
                'userId': 'DE'},
               {'amount': 40.0,
                'dateCreated': '2019-08-08T08:03:14.322540Z',
                'id': 'BA',
                'isCancelled': False,
                'isUsed': False,
                'modelName': 'Booking',
                'quantity': 2,
                'recommendationId': 'BA',
                'reimbursed_amount': 0.0,
                'reimbursement_rule': 'Pas de remboursement au dessus du plafond de 20 000 € '
                                      'par offreur',
                'stock': {'available': 50,
                          'beginningDatetime': None,
                          'bookingLimitDatetime': None,
                          'bookingRecapSent': None,
                          'dateModified': '2019-08-08T08:03:14.791203Z',
                          'dateModifiedAtLastProvider': '2019-08-08T08:03:14.791196Z',
                          'endDatetime': None,
                          'groupSize': 1,
                          'id': 'BA',
                          'idAtProviders': None,
                          'isSoftDeleted': False,
                          'lastProviderId': None,
                          'modelName': 'Stock',
                          'offerId': 'BA',
                          'price': 40.0,
                          'resolvedOffer': {'ageMax': None,
                                            'ageMin': None,
                                            'baseScore': 0,
                                            'bookingEmail': 'offer.booking.email@test.com',
                                            'conditions': None,
                                            'dateCreated': '2019-08-08T08:03:14.322574Z',
                                            'dateModifiedAtLastProvider': '2019-08-08T08:03:14.781558Z',
                                            'description': None,
                                            'durationMinutes': None,
                                            'extraData': {'author': 'Test Author'},
                                            'id': 'BA',
                                            'idAtProviders': '6439289057891@12345678912345',
                                            'isActive': True,
                                            'isFinished': False,
                                            'isFullyBooked': False,
                                            'isNational': False,
                                            'lastProviderId': None,
                                            'mediaUrls': ['test/urls'],
                                            'modelName': 'Offer',
                                            'name': 'Test Book',
                                            'product': {'ageMax': None,
                                                        'ageMin': None,
                                                        'conditions': None,
                                                        'dateModifiedAtLastProvider': '2019-08-08T08:03:14.775065Z',
                                                        'description': None,
                                                        'durationMinutes': None,
                                                        'extraData': {'author': 'Test '
                                                                                'Author'},
                                                        'firstThumbDominantColor': [0, 0, 0],
                                                        'id': 'BA',
                                                        'idAtProviders': '6439289057891',
                                                        'isNational': False,
                                                        'lastProviderId': None,
                                                        'mediaUrls': ['test/urls'],
                                                        'modelName': 'Product',
                                                        'name': 'Test Book',
                                                        'offerType': {'appLabel': 'Films sur '
                                                                                  'supports '
                                                                                  'physiques '
                                                                                  'et VOD',
                                                                      'conditionalFields': [],
                                                                      'description': 'Action, '
                                                                                     'science-fiction, '
                                                                                     'documentaire '
                                                                                     'ou '
                                                                                     'comédie '
                                                                                     'sentimentale '
                                                                                     '? En '
                                                                                     'salle, '
                                                                                     'en '
                                                                                     'plein '
                                                                                     'air ou '
                                                                                     'bien '
                                                                                     'au '
                                                                                     'chaud '
                                                                                     'chez '
                                                                                     'soi ? '
                                                                                     'Et si '
                                                                                     'c’était '
                                                                                     'plutôt '
                                                                                     'cette '
                                                                                     'exposition '
                                                                                     'qui '
                                                                                     'allait '
                                                                                     'faire '
                                                                                     'son '
                                                                                     'cinéma '
                                                                                     '?',
                                                                      'offlineOnly': False,
                                                                      'onlineOnly': False,
                                                                      'proLabel': 'Audiovisuel '
                                                                                  '— films '
                                                                                  'sur '
                                                                                  'supports '
                                                                                  'physiques '
                                                                                  'et VOD',
                                                                      'sublabel': 'Regarder',
                                                                      'type': 'Thing',
                                                                      'value': 'ThingType.AUDIOVISUEL'},
                                                        'owningOffererId': None,
                                                        'thumbCount': 1,
                                                        'thumbUrl': 'https://storage.gra3.cloud.ovh.net/v1/AUTH_688df1e25bd84a48a3804e7fa8938085/storage-pc-dev/thumbs/products/BA',
                                                        'type': 'ThingType.AUDIOVISUEL',
                                                        'url': None},
                                            'productId': 'BA',
                                            'type': 'ThingType.AUDIOVISUEL',
                                            'url': None,
                                            'venueId': 'AM'}},
                'stockId': 'BA',
                'token': None,
                'user': {'email': 'test@email.com', 'firstName': 'John', 'lastName': 'Doe'},
                'userId': 'DE'},
               {'amount': 20.0,
                'dateCreated': '2019-08-08T08:03:14.322540Z',
                'id': 'A4',
                'isCancelled': False,
                'isUsed': False,
                'modelName': 'Booking',
                'quantity': 2,
                'recommendationId': 'A4',
                'reimbursed_amount': 0.0,
                'reimbursement_rule': 'Pas de remboursement au dessus du plafond de 20 000 € '
                                      'par offreur',
                'stock': {'available': 10,
                          'beginningDatetime': '2019-08-11T08:03:14.322563Z',
                          'bookingLimitDatetime': '2019-08-11T07:03:14.322567Z',
                          'bookingRecapSent': None,
                          'dateModified': '2019-08-08T08:03:14.789045Z',
                          'dateModifiedAtLastProvider': '2019-08-08T08:03:14.789038Z',
                          'endDatetime': '2019-08-11T10:03:14.322565Z',
                          'groupSize': 1,
                          'id': 'A4',
                          'idAtProviders': None,
                          'isSoftDeleted': False,
                          'lastProviderId': None,
                          'modelName': 'Stock',
                          'offerId': 'A4',
                          'price': 20.0,
                          'resolvedOffer': {'ageMax': None,
                                            'ageMin': None,
                                            'baseScore': 0,
                                            'bookingEmail': 'offer.booking.email@test.com',
                                            'conditions': None,
                                            'dateCreated': '2019-08-08T08:03:14.322576Z',
                                            'dateModifiedAtLastProvider': '2019-08-08T08:03:14.778957Z',
                                            'description': None,
                                            'durationMinutes': 60,
                                            'extraData': None,
                                            'id': 'A4',
                                            'idAtProviders': None,
                                            'isActive': True,
                                            'isFinished': False,
                                            'isFullyBooked': False,
                                            'isNational': False,
                                            'lastProviderId': None,
                                            'mediaUrls': [],
                                            'modelName': 'Offer',
                                            'name': 'Mains, sorts et papiers',
                                            'product': {'ageMax': None,
                                                        'ageMin': None,
                                                        'conditions': None,
                                                        'dateModifiedAtLastProvider': '2019-08-08T08:03:14.772579Z',
                                                        'description': None,
                                                        'durationMinutes': 60,
                                                        'extraData': None,
                                                        'firstThumbDominantColor': None,
                                                        'id': 'A4',
                                                        'idAtProviders': None,
                                                        'isNational': False,
                                                        'lastProviderId': None,
                                                        'mediaUrls': [],
                                                        'modelName': 'Product',
                                                        'name': 'Mains, sorts et papiers',
                                                        'offerType': {'appLabel': 'Évenements, '
                                                                                  'Rencontres, '
                                                                                  'Concours',
                                                                      'conditionalFields': [],
                                                                      'description': 'Résoudre '
                                                                                     'l’énigme '
                                                                                     'd’un '
                                                                                     'jeu de '
                                                                                     'piste '
                                                                                     'dans '
                                                                                     'votre '
                                                                                     'ville '
                                                                                     '? '
                                                                                     'Jouer '
                                                                                     'en '
                                                                                     'ligne '
                                                                                     'entre '
                                                                                     'amis ? '
                                                                                     'Découvrir '
                                                                                     'cet '
                                                                                     'univers '
                                                                                     'étrange '
                                                                                     'avec '
                                                                                     'une '
                                                                                     'manette '
                                                                                     '?',
                                                                      'offlineOnly': True,
                                                                      'onlineOnly': False,
                                                                      'proLabel': 'Jeux — '
                                                                                  'évenements, '
                                                                                  'rencontres, '
                                                                                  'concours',
                                                                      'sublabel': 'Jouer',
                                                                      'type': 'Event',
                                                                      'value': 'EventType.JEUX'},
                                                        'owningOffererId': None,
                                                        'thumbCount': 0,
                                                        'thumbUrl': 'https://storage.gra3.cloud.ovh.net/v1/AUTH_688df1e25bd84a48a3804e7fa8938085/storage-pc-dev/thumbs/products/A4',
                                                        'type': 'EventType.JEUX',
                                                        'url': None},
                                            'productId': 'A4',
                                            'type': 'EventType.JEUX',
                                            'url': None,
                                            'venueId': 'AM'}},
                'stockId': 'A4',
                'token': None,
                'user': {'email': 'test@email.com', 'firstName': 'John', 'lastName': 'Doe'},
                'userId': 'DE'}]
