import { getCurrentUserUUID } from '../../hocs/with-login/with-react-redux-login'

import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props when user logged in', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'Rt4R45ETEs',
              currentUserUUID: getCurrentUserUUID(),
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'Rt4R45ETEs' })
    })

    it('should return an object of props when user not logged in', () => {
      // given
      const state = { data: { users: [] } }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'ANONYMOUS' })
    })
  })
})
