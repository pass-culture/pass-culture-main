import { selectCurrentUser } from '../selectCurrentUser'

describe('src | selectors | selectCurrentUser', () => {
  it('should return an empty array when there is no stock related to the offer id', () => {
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
