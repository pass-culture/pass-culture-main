import { mapStateToProps } from '../../HeaderContainer'
import { getCurrentUserUUID } from 'with-react-redux-login'

describe('src | components | Layout | Header | HeaderContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          offerers: [],
          users: [{
            publicName: 'super nom',
            currentUserUUID: getCurrentUserUUID(),
          }]
        },
      }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        name: 'super nom',
        offerers: []
      })
    })
  })
})
