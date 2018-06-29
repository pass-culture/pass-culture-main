import createOfferSelector from '../createOffer'
import state from './mockState'

describe('createOfferSelector', () => {
  it.skip('should select the global state', () => {
    // TODO mettre à jour le mock avec des offres
    const expected = {}
    const eventOccurenceId = "AE"
    const selector = createOfferSelector()
    expect(selector(state, eventOccurenceId)).toEqual(expected)
  })
})
