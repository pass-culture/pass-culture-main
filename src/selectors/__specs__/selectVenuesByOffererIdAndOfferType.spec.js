import selectVenuesByOffererIdAndOfferType from '../selectVenuesByOffererIdAndOfferType'

describe('src | selectors | selectVenuesByOffererIdAndOfferType', () => {
  it('should return an array of object', () => {
    // given
    const state = {
      data: {
        venues: [
          {
            address: 'RUE PANACOCO',
            bic: null,
            bookingEmail: 'fake@email.com',
            city: 'Cayenne',
            comment: null,
            dateModifiedAtLastProvider: '2019-09-26T13:34:21.359922Z',
            departementCode: '97',
            firstThumbDominantColor: null,
            iban: null,
            id: 'CE',
            idAtProviders: null,
            isVirtual: false,
            lastProviderId: null,
            latitude: 4.91665,
            longitude: -52.31916,
            managingOffererId: 'BQ',
            modelName: 'Venue',
            nOffers: 10,
            name: 'Espace des Gnoux',
            postalCode: '97300',
            publicName: null,
            siret: '22222223111111',
            thumbCount: 0,
          },
          {
            address: 'RUE PASTEUR',
            bic: null,
            bookingEmail: 'fake@email.com',
            city: 'Cayenne',
            comment: null,
            dateModifiedAtLastProvider: '2019-09-26T13:34:21.359922Z',
            departementCode: '97',
            firstThumbDominantColor: null,
            iban: null,
            id: 'CE',
            idAtProviders: null,
            isVirtual: false,
            lastProviderId: null,
            latitude: 4.91665,
            longitude: -52.31916,
            managingOffererId: 'FGTYRY',
            modelName: 'Venue',
            nOffers: 10,
            name: 'Espace des Gnoux',
            postalCode: '97300',
            publicName: null,
            siret: '22222223111111',
            thumbCount: 0,
          },
        ],
      },
    }

    const offererId = 'BQ'
    const selectedOfferType = {
      appLabel: 'Abonnements',
      description:
        'Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
      id: 10,
      isActive: true,
      offlineOnly: true,
      onlineOnly: false,
      proLabel: 'Cinéma — abonnements',
      sublabel: 'Regarder',
      type: 'Thing',
      value: 'ThingType.CINEMA_ABO',
    }

    // when
    const expected = [
      {
        address: 'RUE PANACOCO',
        bic: null,
        bookingEmail: 'fake@email.com',
        city: 'Cayenne',
        comment: null,
        dateModifiedAtLastProvider: '2019-09-26T13:34:21.359922Z',
        departementCode: '97',
        firstThumbDominantColor: null,
        iban: null,
        id: 'CE',
        idAtProviders: null,
        isVirtual: false,
        lastProviderId: null,
        latitude: 4.91665,
        longitude: -52.31916,
        managingOffererId: 'BQ',
        modelName: 'Venue',
        nOffers: 10,
        name: 'Espace des Gnoux',
        postalCode: '97300',
        publicName: null,
        siret: '22222223111111',
        thumbCount: 0,
      },
    ]
    const result = selectVenuesByOffererIdAndOfferType(state, offererId, selectedOfferType)

    // then
    expect(result).toStrictEqual(expected)
  })
  it('should return an empty array when state contains no venues', () => {
    // given
    const state = {
      data: {
        venues: [],
      },
    }

    // when
    const result = selectVenuesByOffererIdAndOfferType(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array of object when state contains virtual venue', () => {
    // given
    const state = {
      data: {
        venues: [
          {
            isVirtual: true,
          },
        ],
      },
    }

    // when
    const result = selectVenuesByOffererIdAndOfferType(state)

    // then
    const expected = [
      {
        isVirtual: true,
      },
    ]
    expect(result).toStrictEqual(expected)
  })
})
