import { selectCurrentUser } from '../usersSelectors'

describe('users selectors', () => {
  describe('select current user infos', () => {
    describe('when nothing in the store', () => {
      it('should return nothing', () => {
        // given
        const state = {
          data: {},
        }

        // when
        const user = selectCurrentUser(state)

        // then
        expect(user).toBeUndefined()
      })
    })

    describe('when users in the store', () => {
      it('should return the first user', () => {
        // given
        const state = {
          data: {
            users: [
              {
                id: 'EF',
              },
            ],
          },
        }

        // when
        const user = selectCurrentUser(state)

        // then
        expect(user).toStrictEqual({ id: 'EF' })
      })
    })
  })
})
