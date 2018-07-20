import bookingSelector from '../booking'
import state from './mockedState'

describe('bookingSelector', () => {
  //TODO
  it.skip('should select the global state', () => {
    expect(bookingSelector(state)).toEqual({})
  })
})
