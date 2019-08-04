import selectOfferById from '../selectOfferById'

describe('src | selectors | selectOfferById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        offers: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectOfferById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return offer matching id', () => {
    // given
    const state = {
      data: {
        offers: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectOfferById(state, 'bar')

    // then
    expect(result).toBeDefined()
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.offers[1])
  })
})
