import { requestData } from 'redux-saga-data'
import { mapDispatchToProps } from '../ActivationPageContainer'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))
describe('src | components | pages | activation | password | ActivationPageContainer', () => {
  describe('mapStateToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    it('should return two functions', () => {
      // given
      const expectedResult = {
        loginUserAfterPasswordSaveSuccess: expect.anything(),
        sendActivationPasswordForm: expect.anything(),
      }

      // when
      const result = mapDispatchToProps(dispatch)

      // then
      expect(result).toEqual(expectedResult)
    })

    describe('loginUserAfterPasswordSaveSuccess', () => {
      it('should dispatch a requestData action', () => {
        // given
        const actions = mapDispatchToProps(dispatch)
        const failFunction = jest.fn()
        const successFunction = jest.fn()
        const values = {
          email: 'fake email',
          newPassword: 'fake password',
        }
        const config = {
          apiPath: '/users/signin',
          body: { identifier: values.email, password: values.newPassword },
          handleFail: failFunction,
          handleSuccess: successFunction,
          method: 'POST',
        }
        const expectedAction = {
          config,
          type: 'REQUEST_DATA_POST_/USERS/SIGNIN',
        }
        requestData.mockReturnValue(expectedAction)

        // when
        actions.loginUserAfterPasswordSaveSuccess(
          values,
          failFunction,
          successFunction
        )

        // then
        expect(requestData).toHaveBeenCalledWith(config)
        expect(dispatch).toHaveBeenCalledWith(expectedAction)
      })
    })

    describe('sendActivationPasswordForm', () => {
      it('should dispatch a requestData action', () => {
        // given
        const actions = mapDispatchToProps(dispatch)
        const values = {
          email: 'fake email',
          newPassword: 'fake password',
        }
        const failFunction = jest.fn(() => {})
        const successFunction = jest.fn(() => {})
        const config = {
          apiPath: '/users/new-password',
          body: { email: values.email, newPassword: values.newPassword },
          handleFail: failFunction,
          handleSuccess: successFunction,
          method: 'POST',
          stateKey: 'activatedUserCredentials',
        }
        const expectedAction = {
          config,
          type: 'REQUEST_DATA_POST_ACTIVATEDUSERCREDENTIALS',
        }
        requestData.mockReturnValue(expectedAction)

        // when
        actions.sendActivationPasswordForm(
          values,
          () => failFunction,
          () => successFunction
        )

        // then
        expect(requestData).toHaveBeenCalledWith(config)
        expect(dispatch).toHaveBeenCalledWith(expectedAction)
      })
    })
  })
})
