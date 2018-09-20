import cachedSearchSelector from '../search'

//
//  const props = {
// location: {
//   search: "?from_date=1537284802907&keywords=emploi"
// }
// }

// const queryParams = searchSelector(state, ownProps.location.search)
// queryParams = {search: "emploi"}

describe('createOfferSelector', () => {
  let state
  state = {}
  let search

  it('should select the global state', () => {
    search = '?from_date=1537284802907&keywords=emploi'
    const expected = {
      from_date: '1537284802907',
      keywords: 'emploi',
    }
    expect(cachedSearchSelector(state, search)).toEqual(expected)
  })

  it('should select the query Params in the state', () => {
    search = '?from_date=1537284802907&keywords=emploi'
    state = {
      queryParams: {
        from_date: 1537284802907,
        keywords: 'emploi',
      },
    }

    const expected = {
      from_date: '1537284802907',
      keywords: 'emploi',
    }
    expect(cachedSearchSelector(state, search)).toEqual(expected)
  })

  it('should select the query Params in the state', () => {
    search = ''
    state = {}
    const expected = {}
    expect(cachedSearchSelector(state, search)).toEqual(expected)
  })

  // TODO String = null > Error
})
