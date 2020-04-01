import selectFormInitialValuesByProductAndOfferAndOffererAndVenue from '../selectFormInitialValuesByProductAndOfferAndOffererAndVenue'

describe('components | OfferEdition | selectFormInitialValuesByProductAndOfferAndOffererAndVenue', () => {
  it('should build an object using initial values from offer or product (given POST or PATCH context), venue and offerer', () => {
    // given
    const state = {}
    const product = {
      ageMax: null,
      ageMin: null,
      condition: null,
      description: 'PNL n’est plus ce qu’il.elle était',
      durationMinutes: 60,
      extraData: { author: 'Jean-Michel' },
      id: 'FE',
      isDuo: true,
      isNational: true,
      mediaUrls: [],
      name: 'Au bb',
      type: 'EventType.CINEMA',
      url: undefined,
    }
    const offer = {}
    const offerer = {
      id: 'BF',
    }
    const venue = {
      id: 'CE',
    }

    // when
    const value = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
      state,
      product,
      offer,
      offerer,
      venue
    )

    // then
    const expectedValue = {
      ageMax: null,
      ageMin: null,
      bookingEmail: undefined,
      condition: null,
      description: 'PNL n’est plus ce qu’il.elle était',
      durationMinutes: 60,
      extraData: { author: 'Jean-Michel' },
      isDuo: true,
      isNational: true,
      mediaUrls: [],
      name: 'Au bb',
      offererId: 'BF',
      type: 'EventType.CINEMA',
      url: undefined,
      venueId: 'CE',
    }
    expect(value).toStrictEqual(expectedValue)
  })

  it('should build an object taking info from product when creating new offer', () => {
    // given
    const state = {}
    const product = {
      description: 'PNL n’est plus ce qu’il.elle était',
    }
    const offer = {}
    const offerer = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
      state,
      product,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toStrictEqual(product.description)
  })

  it('should build an offer taking info from offer when updating offer', () => {
    // given
    const state = {}
    const product = {
      description: 'PNL n’est plus ce qu’il.elle était',
    }
    const offer = {
      description: '',
      id: 'AE',
    }
    const offerer = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
      state,
      product,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toStrictEqual(offer.description)
  })
})
