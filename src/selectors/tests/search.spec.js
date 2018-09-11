import cachedSearchSelector from '../search'

describe('createOfferSelector', () => {
  const state = {}
  it('should select the global state', () => {
    const search = 'search=FakeText'
    const expected = {
      search: 'FakeText',
    }
    expect(cachedSearchSelector(state, search)).toEqual(expected)
  })
})
