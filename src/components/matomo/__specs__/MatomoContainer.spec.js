import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        user: {
          id: 'TY7',
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ user: { id: 'TY7' } })
    })
  })
})
