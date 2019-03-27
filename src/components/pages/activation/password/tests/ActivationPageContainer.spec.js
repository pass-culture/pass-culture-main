import { requestData } from 'redux-saga-data'
import { mapDispatchToProps, mapStateToProps } from '../ActivationPageContainer'
import { isValidToken } from '../../../../../utils/http/client'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))
jest.mock('../../../../../utils/http/client', () => ({
  isValidToken: jest.fn(),
}))
describe('src | components | pages | activation | password | ActivationPageContainer', () => {
  describe('mapDispatchToProps', () => {
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

  describe('mapStateToProps', () => {
    describe('isValidUrl', () => {
      it('should return false when no email is given', () => {
        // given
        const location = {}
        const match = {
          params: {
            token: 'fake token',
          },
        }
        const params = {
          location,
          match,
        }

        // when
        const result = mapStateToProps({}, params)

        // then
        expect(result).toHaveProperty('isValidUrl', false)
      })

      it('should return false when no token is given', () => {
        // given
        const location = {
          search: '?email=fake@example.net',
        }
        const match = {}
        const params = {
          location,
          match,
        }

        // when
        const result = mapStateToProps({}, params)

        // then
        expect(result).toHaveProperty('isValidUrl', false)
      })

      it('should return false when neither token nor email are given', () => {
        // given
        const location = {}
        const match = {}
        const params = {
          location,
          match,
        }

        // when
        const result = mapStateToProps({}, params)

        // then
        expect(result).toHaveProperty('isValidUrl', false)
      })

      it('should return true when token and email are given', () => {
        // given
        const location = {
          search: '?email=fake@example.net',
        }
        const match = {
          params: {
            token: 'fake token',
          },
        }
        const params = {
          location,
          match,
        }

        // when
        const result = mapStateToProps({}, params)

        // then
        expect(result).toHaveProperty('isValidUrl', true)
      })
    })

    describe('initialValues', () => {
      it('should map email from query params', () => {
        // given
        const location = { search: '?email=prenom@example.net' }

        // when
        const { initialValues } = mapStateToProps({}, { location, match: {} })

        // then
        expect(initialValues).toHaveProperty('email', 'prenom@example.net')
      })

      it('should map token from router params', () => {
        // given
        const location = { search: '?email=prenom@example.net' }
        const match = { params: { token: 'my-precious-token' } }

        // when
        const { initialValues } = mapStateToProps({}, { location, match })

        // then
        expect(initialValues).toHaveProperty('token', 'my-precious-token')
      })
    })

    describe('isTokenValid', () => {
      it('should map isTokenValid as true', () => {
        // given
        const match = { params: { token: 'my-precious-token' } }
        const tokenStatusResolvedFromAPI = true
        isValidToken.mockReturnValue(
          Promise.resolve(tokenStatusResolvedFromAPI)
        )

        // when
        const props = mapStateToProps({}, { location: {}, match })

        // then
        expect(props).toHaveProperty('isValidToken', tokenStatusResolvedFromAPI)
      })

      it('should evaluate token validity from URL', () => {
        // given
        const match = { params: { token: 'my-precious-token' } }

        // when
        mapStateToProps({}, { location: {}, match })

        // then
        expect(isValidToken).toHaveBeenCalledWith('my-precious-token')
      })
    })
  })
})
