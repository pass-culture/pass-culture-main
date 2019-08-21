import { getCurrentUserUUID } from 'with-react-redux-login'

import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props when user logged in', () => {
      // given
      const state = {
        data: {
          users: [
            {
              canBookFreeOffers: true,
              id: 'TY7',
              currentUserUUID: getCurrentUserUUID(),
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ id: 'TY7', canBookFreeOffers: true })
    })
    it('should return an object of props when user not logged in', () => {
      // given
      const state = { data: { users: [] } }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ id: undefined, canBookFreeOffers: undefined })
    })
  })
})
