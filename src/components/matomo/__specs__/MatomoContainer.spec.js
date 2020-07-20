import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props when user logged in', () => {
      // given
      const state = {
        currentUser: {
          id: 'Rt4R45ETEs',
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        userId: 'Rt4R45ETEs',
      })
    })

    it('should return an object of props when user not logged in', () => {
      // given
      const state = {
        currentUser: null,
      }
      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        userId: 'ANONYMOUS',
      })
    })
  })
})
