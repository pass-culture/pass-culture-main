import recommendationQuerySelector from '../recommendationQuery'
import state from './mockedState'

describe.skip('recommendationQuerySelector', () => {
  //TODO
  it.skip('should select the global state', () => {
    expect(recommendationQuerySelector(state)).toEqual({})
  })
})
