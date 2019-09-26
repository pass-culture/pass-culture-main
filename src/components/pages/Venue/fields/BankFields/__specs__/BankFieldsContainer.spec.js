import { mapStateToProps } from '../BankFieldsContainer'
import state from '../../../../../utils/mocks/state'

describe('src | components | pages | Venue | fields | BankFieldsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with the right props', () => {
      // given
      const props = {
        match: {
          params: {
            offererId: 'FE',
          },
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        adminUserOfferer: {
          offererId: 'FE',
          rights: 'admin',
          userId: 'FE',
        },
      })
    })
  })
})
