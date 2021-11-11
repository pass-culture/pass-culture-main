import { mapDispatchToProps } from '../SignInContainer'

jest.mock('../../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual('../../../../utils/fetch-normalize-data/reducers/data/actionCreators')

  return {
    requestData: _requestData,
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
        password: 'abcdef123',
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
          apiPath: '/beneficiaries/signin',
          body: { identifier: 'pc-beneficiary@example.com', password: 'abcdef123' },
          handleFail: true,
          handleSuccess: true,
          method: 'POST',
        },
        type: 'REQUEST_DATA_POST_/BENEFICIARIES/SIGNIN',
      })
      expect(result).toBeInstanceOf(Promise)
    })
  })
})
