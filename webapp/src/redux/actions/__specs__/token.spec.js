import { setTokenStatus } from '../token'

describe('actions | token', () => {
  describe('actions', () => {
    it('should return an action of type SET_TOKEN_STATUS', () => {
      // given
      const tokenStatus = true

      // when
      const result = setTokenStatus(tokenStatus)

      // then
      expect(result).toStrictEqual({
        payload: true,
        type: 'SET_TOKEN_STATUS',
      })
    })
  })
})
