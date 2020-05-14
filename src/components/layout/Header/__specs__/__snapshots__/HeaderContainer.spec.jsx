import { mapStateToProps } from '../../HeaderContainer'

describe('src | components | Layout | Header | HeaderContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          offerers: [],
          users: [
            {
              publicName: 'super nom',
            },
          ],
        },
      }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        name: 'super nom',
        offerers: [],
      })
    })
  })
})
