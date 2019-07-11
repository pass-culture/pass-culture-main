import { mapStateToProps } from '../BankFieldsContainer'
import { selectCurrentUser } from 'with-login'
import state from '../../../../../utils/mocks/state'

describe('src | components | pages | Venue | fields | BankFieldsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with the right props', () => {
      // given
      const props = {
        match: {
          params: {
            offererId: 'FE'
          }
        }
      }
      selectCurrentUser.currentUserUUID = '22a18e44-710c-45cd-b442-34d8ff417fac'

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        adminUserOfferer: {
          offererId: 'FE',
          rights: 'RightsType.admin',
          userId: 'FE'
        }
      })
    })
  })
})
