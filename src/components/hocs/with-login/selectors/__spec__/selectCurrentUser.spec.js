import selectCurrentUser from '../selectCurrentUser'

describe('createCurrentUserSelector', () => {
  it('should select the global state', () => {
    // given
    const state = {
      data: {
        users: [{
          id: 'BE'
        }]
      },
    }

    // when
    const result = selectCurrentUser(
      state,

    )
    const expected = {
      id: 'BE'
    }

    // then
    expect(result).toEqual(expected)
  })
})
