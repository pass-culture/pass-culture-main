import { selectCurrentUser, selectIsUserAdmin } from '../usersSelectors'

describe('users selectors', () => {
  describe('select if user is admin', () => {
    it('should return false when state contains no users', () => {
      // given
      const state = {
        data: {
          users: [],
        },
      }

      // when
      const result = selectIsUserAdmin(state)

      // then
      expect(result).toBe(false)
    })

    it('should return true when state contain an admin user', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'FA',
              isAdmin: true,
            },
          ],
        },
      }

      // when
      const result = selectIsUserAdmin(state)

      // then
      expect(result).toBe(true)
    })

    it('should return false when state contain no admin user', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'EF',
              isAdmin: false,
            },
          ],
        },
      }

      // when
      const result = selectIsUserAdmin(state)

      // then
      expect(result).toBe(false)
    })
  })

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
