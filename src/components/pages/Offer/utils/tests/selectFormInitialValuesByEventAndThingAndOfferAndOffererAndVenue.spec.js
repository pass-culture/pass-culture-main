import { selectFormInitialValuesByProductAndOfferAndOffererAndVenue } from '../selectFormInitialValuesByProductAndOfferAndOffererAndVenue'

describe('src | components | pages | Offer | utils | selectFormInitialValuesByProductAndOfferAndOffererAndVenue', () => {
  it('should build an object using initial values from offer or product (given POST or PATCH context), venue and offerer', () => {
    // given
    const state = {}
    const event = {
      ageMax: null,
      ageMin: null,
      condition: null,
      description: "PNL n'est plus ce qu'il.elle était",
      durationMinutes: 60,
      extraData: { author: 'Jean-Michel' },
      id: 'FE',
      isNational: true,
      mediaUrls: [],
      name: 'Au bb',
      type: 'EventType.CINEMA',
      url: undefined,
    }
    const product = {}
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
      event,
      product,
      offer,
      offerer,
      venue
    )
    const expectedValue = {
      ageMax: null,
      ageMin: null,
      bookingEmail: undefined,
      condition: null,
      description: "PNL n'est plus ce qu'il.elle était",
      durationMinutes: 60,
      extraData: { author: 'Jean-Michel' },
      isNational: true,
      mediaUrls: [],
      name: 'Au bb',
      offererId: offerer.id,
      type: 'EventType.CINEMA',
      url: undefined,
      venueId: venue.id,
    }

    // then
    expect(value).toEqual(expectedValue)
  })

  it('should build an object taking info from product when creating new offer', () => {
    // given
    const state = {}
    const event = {
      description: "PNL n'est plus ce qu'il.elle était",
    }
    const product = {}
    const offer = {}
    const offerer = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
      state,
      event,
      product,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toEqual(event.description)
  })

  it('should build an offer taking info from offer when updating offer', () => {
    // given
    const state = {}
    const event = {
      description: "PNL n'est plus ce qu'il.elle était",
    }
    const offer = {
      description: '',
      id: 'AE',
    }
    const offerer = {}
    const product = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
      state,
      event,
      product,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toEqual(offer.description)
  })
})
