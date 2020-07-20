import { selectCurrentUser } from '../currentUserSelector'
import User from '../../../components/pages/profile/ValueObjects/User'

describe('currentUser selector', () => {
  describe('select current user infos', () => {
    describe('when nothing in the store', () => {
      it('should return nothing', () => {
        // given
        const state = {}

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
          currentUser: {
            id: 'EF',
          },
        }

        // when
        const user = selectCurrentUser(state)

        // then
        expect(user).toStrictEqual(
          new User({
            departementCode: undefined,
            email: undefined,
            expenses: undefined,
            firstName: undefined,
            id: 'EF',
            lastName: undefined,
            publicName: undefined,
            wallet_balance: undefined,
            wallet_date_created: undefined,
          })
        )
      })
    })
  })
})
