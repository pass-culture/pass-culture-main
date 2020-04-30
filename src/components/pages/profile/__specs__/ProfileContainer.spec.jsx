import { mapStateToProps } from '../ProfileContainer'

describe('profile container', () => {
  describe('mapStateToProps', () => {
    it('should return an object containing current user', () => {
      // given
      const state = {
        data: {
          users: [
            {
              firstName: 'José',
              lastName: 'Lafrite',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        currentUser: {
          firstName: 'José',
          lastName: 'Lafrite',
        },
      })
    })
  })
})
