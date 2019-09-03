import { selectCurrentUser } from '../selectCurrentUser'

describe('src | selectors | selectCurrentUser', () => {
  it('should return current user id', () => {
    // given
    const state = {
      user: {
        id: 'FG6',
      },
    }

    // when
    const result = selectCurrentUser(state)

    // then
    expect(result).toStrictEqual({ id: 'FG6' })
  })
})
