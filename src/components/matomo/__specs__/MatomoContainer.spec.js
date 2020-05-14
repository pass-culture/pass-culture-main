import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props when user is logged in', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'TY7',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'TY7' })
    })

    it('should return an object of props when user is logged out', () => {
      // given
      const state = {
        data: {
          users: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'ANONYMOUS' })
    })
  })
})
