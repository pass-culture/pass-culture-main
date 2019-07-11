import { currentUserUUID } from 'with-react-redux-login'

import { mapStateToProps } from '../ProfileFormContainer'

describe('src | components | pages | profile | forms | ProfileFormContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const id = '1'
      const publicName = 'fake name'
      const state = {
        data: { users: [{ currentUserUUID, id, publicName }] },
      }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        initialValues: {
          publicName: 'fake name',
        },
      })
    })
  })
})
