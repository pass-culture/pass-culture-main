import { selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue } from '../selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue'

describe('src | components | pages | Offer | utils | selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue', () => {
  it('should take info from event or thing when offer has no idea, ie isCreatedEntity', () => {
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
    const thing = {}
    const offer = {}
    const offerer = {
      id: 'BF',
    }
    const venue = {
      id: 'CE',
    }

    // when
    const value = selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue(
      state,
      event,
      thing,
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

  it('should take info from event or thing when offer has no idea, ie isCreatedEntity', () => {
    // given
    const state = {}
    const event = {
      description: "PNL n'est plus ce qu'il.elle était",
    }
    const thing = {}
    const offer = {}
    const offerer = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue(
      state,
      event,
      thing,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toEqual(event.description)
  })

  it('should take info from offer when offer.id, ie isModifiedEntity', () => {
    // given
    const state = {}
    const event = {
      description: "PNL n'est plus ce qu'il.elle était",
    }
    const thing = {}
    const offer = {
      description: '',
      id: 'AE',
    }
    const offerer = {}
    const venue = {}

    // when
    const value = selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue(
      state,
      event,
      thing,
      offer,
      offerer,
      venue
    )

    // then
    expect(value.description).toEqual(offer.description)
  })
})
