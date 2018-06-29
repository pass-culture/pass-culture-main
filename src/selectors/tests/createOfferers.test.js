import createOfferersSelector from '../createOfferers'
import state from './mockState'

describe('createOfferersSelector', () => {
  it('should select the global state', () => {
    const expected = state.data.offerers
    const selector = createOfferersSelector()
    expect(selector(state)).toEqual(expected)
  })
})
