import { selectOfferById } from '../selectors'

describe('offersSelectors', () => {
  const state = {
    offers: {
      list: [
        {
          id: 'AXBQ',
          bookingEmail: null,
          dateCreated: '2018-11-13T09:54:56.103080Z',
          dateModifiedAtLastProvider: '2018-11-13T09:54:56.103073Z',
          isEvent: false,
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Offer',
          productId: 'V4',
          isThing: true,
          venueId: 'AYJA',
          eventOccurrencesIds: [],
          mediationsIds: [],
          stocksIds: ['DCRA'],
        },
      ],
    },
  }

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
        offers: {},
      }

      // when
      const offer = selectOfferById(state, offerId)

      // then
      expect(offer).toBeUndefined()
    })
  })
})
