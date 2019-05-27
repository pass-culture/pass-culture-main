import { selectCurrentUser } from 'with-login'
import { mapStateToProps } from '../ProfileFormContainer'

describe('src | components | pages | profile | forms | ProfileFormContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const id = '1'
      const currentUserUUID = 'ABC'
      const publicName = 'fake name'
      const state = {
        data: { users: [{ currentUserUUID, id, publicName }] },
      }
      selectCurrentUser.currentUserUUID = currentUserUUID

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toEqual({
        initialValues: {
          publicName: 'fake name',
        },
      })
    })
  })
})
