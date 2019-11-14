import { selectOfferById } from '../offersSelectors'
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
