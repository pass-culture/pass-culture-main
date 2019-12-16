import { mapDispatchToProps } from '../SignInContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
  }
})
describe('container | SignInContainer', () => {
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('mapDispatchToProps', () => {
    it('should dispatch an action for user sign in with the right parameters', () => {
      // given
      const values = {
        identifier: 'pc-beneficiary@example.com',
        password: 'abcdef123'
      }
      const functions = mapDispatchToProps(dispatch)
      const { signIn } = functions

      // when
      const result = signIn(
        values,
        jest.fn().mockImplementationOnce(() => true),
        jest.fn().mockImplementationOnce(() => true)
      )

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/users/signin',
          body: { identifier: 'pc-beneficiary@example.com', password: 'abcdef123' },
          handleFail: true,
          handleSuccess: true,
          method: 'POST'
        },
        type: 'REQUEST_DATA_POST_/USERS/SIGNIN'
      })
      expect(result).toBeInstanceOf(Promise)
    })
  })
})
