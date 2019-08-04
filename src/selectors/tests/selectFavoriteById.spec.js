import selectFavoriteById from '../selectFavoriteById'

describe('src | selectors | selectFavoriteById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        favorites: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectFavoriteById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return favorite matching id', () => {
    // given
    const state = {
      data: {
        favorites: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectFavoriteById(state, 'bar')

    // then
    expect(result).toBeDefined()
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.favorites[1])
  })
})
