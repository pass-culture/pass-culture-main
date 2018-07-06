import offerersSelector from '../offerers'
import state from './mockState'

describe('createOfferersSelector', () => {
  it('should select the global state', () => {
    const expected = state.data.offerers
    expect(offerersSelector(state)).toEqual(expected)
  })
})
