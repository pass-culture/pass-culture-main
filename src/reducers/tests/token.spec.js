import tokenReducer, { setTokenStatus } from '../token'

describe('src | reducers | token  ', () => {
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

  describe('reducer', () => {
    it('should return initial value when no action matches', () => {
      // when
      const nextState = tokenReducer()

      // then
      expect(nextState).toStrictEqual({
        hasBeenChecked: false,
        isValid: false,
      })
    })

    describe('when a SET_TOKEN_STATUS event is received', () => {
      it('should change mark token as checked and as valid', () => {
        // when
        const nextState = tokenReducer(
          {},
          { payload: true, type: 'SET_TOKEN_STATUS' }
        )

        // then
        expect(nextState).toStrictEqual({
          hasBeenChecked: true,
          isValid: true,
        })
      })

      it('should change mark token as checked and invalid', () => {
        // when
        const nextState = tokenReducer(
          {},
          { payload: false, type: 'SET_TOKEN_STATUS' }
        )

        // then
        expect(nextState).toStrictEqual({
          hasBeenChecked: true,
          isValid: false,
        })
      })
    })
  })
})
