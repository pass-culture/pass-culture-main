import { mapStateToProps } from '../OfferItemContainer'

import state from '../../../../utils/mocks/state'

describe('mapStateToProps', () => {
  let ownProps

  beforeEach(() => {
    ownProps = {
      offer: {
        offerId: 'UU',
        productId: 'LY',
        stockAlertMessage: 'encore 10 en stock',
        venueId: 'DA',
      },
    }
  })

  it('should return the value aggregatedStock', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = {
      available: 0,
      groupSizeMax: 0,
      groupSizeMin: 0,
      priceMax: 0,
      priceMin: 0,
    }

    // then
    expect(result.aggregatedStock).toStrictEqual(expected)
  })

  it('should return the value maxDate', () => {
    // given

    // when
    const result = mapStateToProps(state, ownProps)
    const expected = null

    // then
    expect(result.maxDate).toStrictEqual(expected)
  })

  it('should return the value mediations', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = {
      authorId: null,
      backText: 'Some back test',
      credit: null,
      dateCreated: '2019-03-07T10:39:23.560464Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:08.324689Z',
      firstThumbDominantColor: [0, 0, 0],
      frontText: 'Some front text',
      id: 'H4',
      idAtProviders: null,
      isActive: true,
      lastProviderId: null,
      modelName: 'Mediation',
      offerId: 'UU',
      thumbCount: 1,
      tutoIndex: null,
    }

    // then
    expect(result.mediations[0]).toStrictEqual(expected)
  })

  it('should return an object of prop product', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = {
      dateModifiedAtLastProvider: '2019-03-07T10:40:03.865368Z',
      description:
        'Ainsi la personne avec qui elle avait confessé qu’elle allait goûter, avec qui elle vous avait supplié de la laisser goûter, cette personne, raison avouée par la nécessité, ce n’était pas elle, c’était une autre, c’était encore autre chose ! Autre chose, quoi ? Une autre, qui ?',
      extraData: {
        author: 'Eloise Jomenrency',
      },
      firstThumbDominantColor: [0, 0, 0],
      id: 'LY',
      idAtProviders: '1297',
      isNational: true,
      lastProviderId: null,
      mediaUrls: ['test/urls'],
      modelName: 'Product',
      name: 'Dormons peu soupons bien',
      offerType: {
        description:
          'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
        label: 'Jeux Vidéo',
        offlineOnly: false,
        onlineOnly: true,
        sublabel: 'Jouer',
        type: 'Thing',
        value: 'ThingType.JEUX_VIDEO',
      },
      thumbCount: 1,
      url: 'https://ilestencoretemps.fr/',
    }

    // then
    expect(result.product).toStrictEqual(expected)
  })

  it('should return the value stocks', () => {
    // when

    const result = mapStateToProps(state, ownProps)
    const expected = []

    // then
    expect(result.stocks).toStrictEqual(expected)
  })

  it('should return an object of prop offerer', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = {
      address: 'RUE DES SAPOTILLES',
      bic: 'QSDFGH8Z566',
      city: 'Cayenne',
      dateCreated: '2019-03-07T10:39:23.560414Z',
      dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
      firstThumbDominantColor: null,
      iban: 'FR7630001007941234567890185',
      id: 'BA',
      idAtProviders: null,
      isActive: true,
      isValidated: true,
      lastProviderId: null,
      modelName: 'Offerer',
      nOffers: 5,
      name: 'Bar des amis',
      postalCode: '97300',
      siren: '222222233',
      thumbCount: 0,
      validationToken: null,
    }

    // then
    expect(result.offerer).toStrictEqual(expected)
  })

  it('should return the value of offerTypeLabel', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = 'Jeux Vidéo'

    // then
    expect(result.offerTypeLabel).toStrictEqual(expected)
  })

  it('should return the value of stockAlertMessage', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = 'encore 10 en stock'

    // then
    expect(result.stockAlertMessage).toStrictEqual(expected)
  })

  it('should return an object of prop venue', () => {
    // when
    const result = mapStateToProps(state, ownProps)
    const expected = {
      address: null,
      bookingEmail: 'john.doe@test.com',
      city: null,
      comment: null,
      dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
      departementCode: null,
      firstThumbDominantColor: null,
      id: 'DA',
      idAtProviders: null,
      isValidated: true,
      isVirtual: true,
      lastProviderId: null,
      latitude: 48.83638,
      longitude: 2.40027,
      managingOffererId: 'BA',
      modelName: 'Venue',
      name: 'Le Sous-sol (Offre en ligne)',
      postalCode: null,
      siret: null,
      thumbCount: 0,
      validationToken: null,
    }

    // then
    expect(result.venue).toStrictEqual(expected)
  })
})
