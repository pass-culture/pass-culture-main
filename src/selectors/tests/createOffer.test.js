import offerSelector from '../offer'
import state from './mockState'

describe('createOfferSelector', () => {
  it.skip('should select the global state', () => {
    // TODO mettre à jour le mock avec des offres
    const expected = {}
    const eventOccurrenceId = 'AE'
    expect(offerSelector(state, eventOccurrenceId)).toEqual(expected)
  })
})
