import { selectDigitalOffers, selectOfferById, selectOffersByVenueId } from '../offersSelectors'
import state from './mockState.json'

describe('selectOfferById', () => {
  it('should select an offer given an id', () => {
    // given
    const offerId = 'AXBQ'

    // when
    const offer = selectOfferById(state, offerId)

    // then
    expect(offer.id).toStrictEqual(offerId)
  })

  it('should return no offer when there is no offer related to the given offer id', () => {
    // given
    const offerId = 'M4'

    // when
    const offer = selectOfferById(state, offerId)

    // then
    expect(offer).toBeUndefined()
  })

  it('should return no offer when state is not initialized', () => {
    // given
    const offerId = 'AXBQ'
    const state = {
      data: {},
    }

    // when
    const offer = selectOfferById(state, offerId)

    // then
    expect(offer).toBeUndefined()
  })
})

describe('selectDigitalOffers', () => {
  it('should return an empty array when state contains no offers', () => {
    // given
    const state = {
      data: {
        offers: [],
      },
    }

    // when
    const result = selectDigitalOffers(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array containing only digital offers', () => {
    // given
    const state = {
      data: {
        offers: [
          {
            id: 'A8HQ',
            isDigital: true,
          },
          {
            id: 'A8RQ',
            isDigital: false,
          },
          {
            id: 'AVGQ',
            isDigital: false,
          },
        ],
      },
    }

    // when
    const result = selectDigitalOffers(state)

    // then
    expect(result).toStrictEqual([
      {
        id: 'A8HQ',
        isDigital: true,
      },
    ])
  })
})

describe('selectOffersByVenueId', () => {
  it('should return an empty array when state contains no offers', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {
        offer: [],
      },
    }

    // when
    const result = selectOffersByVenueId(state, venueId)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array of physical offers matching venueId', () => {
    // given
    const venueId = 'CU'
    const state = {
      data: {
        offers: [
          {
            id: 'A8HQ',
            venueId: 'CU',
          },
          {
            id: 'A8RQ',
            venueId: 'CU',
          },
          {
            id: 'AVGQ',
            venueId: 'B9',
          },
        ],
      },
    }

    // when
    const result = selectOffersByVenueId(state, venueId)

    // then
    expect(result).toStrictEqual([
      {
        id: 'A8HQ',
        venueId: 'CU',
      },
      {
        id: 'A8RQ',
        venueId: 'CU',
      },
    ])
  })
})
