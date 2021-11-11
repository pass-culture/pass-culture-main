import token from '../token'

describe('reducers | token', () => {
  it('should return initial value when no action matches', () => {
    // when
    const nextState = token()

    // then
    expect(nextState).toStrictEqual({
      hasBeenChecked: false,
      isValid: false,
    })
  })

  describe('when a SET_TOKEN_STATUS event is received', () => {
    it('should change mark token as checked and as valid', () => {
      // when
      const nextState = token({}, { payload: true, type: 'SET_TOKEN_STATUS' })

      // then
      expect(nextState).toStrictEqual({
        hasBeenChecked: true,
        isValid: true,
      })
    })

    it('should change mark token as checked and invalid', () => {
      // when
      const nextState = token({}, { payload: false, type: 'SET_TOKEN_STATUS' })

      // then
      expect(nextState).toStrictEqual({
        hasBeenChecked: true,
        isValid: false,
      })
    })
  })
})
