import { requestData } from 'redux-saga-data'

import { mapDispatchToProps, mapStateToProps } from '../PasswordFormContainer'
import { validateToken, setTokenStatus } from '../../../../../reducers/token'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))

jest.mock('../../../../../reducers/token', () => ({
  setTokenStatus: jest.fn(param => ({ payload: param, type: 'ACTION' })),
  validateToken: jest.fn(),
}))

describe('src | components | pages | activation | Password | PasswordFormContainer', () => {
  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    it('should return three functions', () => {
      // given
      const expectedResult = {
        checkTokenIsValid: expect.anything(Function),
        loginUserAfterPasswordSaveSuccess: expect.anything(Function),
        sendPassword: expect.anything(Function),
      }

      // when
      const result = mapDispatchToProps(dispatch)

      // then
      expect(result).toStrictEqual(expectedResult)
    })

    describe('checkTokenIsValid', () => {
      it('should verify token validity', async () => {
        // given
        const tokenStatus = true
        const token = 'HDUIV21I'
        validateToken.mockResolvedValue(tokenStatus)

        // when
        await mapDispatchToProps(dispatch).checkTokenIsValid(token)

        // then
        expect(validateToken).toHaveBeenCalledWith(token, dispatch)
      })

      it('should update token status when it is valid', async () => {
        // given
        const tokenStatus = true
        const token = 'HDUIV21I'
        validateToken.mockResolvedValue(tokenStatus)

        // when
        await mapDispatchToProps(dispatch).checkTokenIsValid(token)

        // then
        expect(dispatch).toHaveBeenCalledWith(setTokenStatus(tokenStatus))
      })

      it('should update token status when it is invalid', async () => {
        // given
        const tokenStatus = false
        const token = 'HDUIV21I'
        validateToken.mockResolvedValue(tokenStatus)

        // when
        await mapDispatchToProps(dispatch).checkTokenIsValid(token)

        // then
        expect(dispatch).toHaveBeenCalledWith(setTokenStatus(tokenStatus))
      })
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
        actions.loginUserAfterPasswordSaveSuccess(values, failFunction, successFunction)

        // then
        expect(requestData).toHaveBeenCalledWith(config)
        expect(dispatch).toHaveBeenCalledWith(expectedAction)
      })
    })

    describe('sendPassword', () => {
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
        actions.sendPassword(values, () => failFunction, () => successFunction)

        // then
        expect(requestData).toHaveBeenCalledWith(config)
        expect(dispatch).toHaveBeenCalledWith(expectedAction)
      })
    })
  })

  describe('mapStateToProps', () => {
    let state
    beforeEach(() => {
      state = {
        token: {},
      }
    })

    describe('isValidUrl', () => {
      it('should return false when no email is given', () => {
        // given
        const location = {}
        const match = {
          params: {
            token: 'fake token',
          },
        }
        const query = { parse: () => ({}) }
        const ownProps = {
          location,
          match,
          query,
        }

        // when
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result).toHaveProperty('isValidUrl', false)
      })

      it('should return false when no token is given', () => {
        // given
        const location = {
          search: '?email=fake@example.net',
        }
        const match = {
          params: {},
        }
        const query = { parse: () => ({}) }
        const params = {
          location,
          match,
          query,
        }

        // when
        const result = mapStateToProps(state, params)

        // then
        expect(result).toHaveProperty('isValidUrl', false)
      })

      it('should return false when neither token nor email are given', () => {
        // given
        const location = {}
        const match = {
          params: {},
        }
        const query = { parse: () => ({}) }
        const params = {
          location,
          match,
          query,
        }

        // when
        const result = mapStateToProps(state, params)

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
        const query = {
          parse: () => ({
            email: 'fake@example.net',
          }),
        }
        const ownProps = {
          location,
          match,
          query,
        }

        // when
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result).toHaveProperty('isValidUrl', true)
      })
    })

    describe('initialValues', () => {
      it('should map email from query params', () => {
        // given
        const location = { search: '?email=prenom@example.net' }
        const ownProps = {
          location,
          match: { params: {} },
          query: {
            parse: () => ({
              email: 'prenom@example.net',
            }),
          },
        }

        // when
        const { initialValues } = mapStateToProps(state, ownProps)

        // then
        expect(initialValues).toHaveProperty('email', 'prenom@example.net')
      })

      it('should map token from router params', () => {
        // given
        const location = { search: '?email=prenom@example.net' }
        const match = { params: { token: 'my-precious-token' } }
        const query = { parse: () => ({}) }
        const ownProps = {
          location,
          match,
          query,
        }

        // when
        const { initialValues } = mapStateToProps(state, ownProps)

        // then
        expect(initialValues).toHaveProperty('token', 'my-precious-token')
      })
    })

    describe('hasTokenBeenChecked', () => {
      it('should mark if token has been checked', () => {
        // given
        state = { token: { hasBeenChecked: false } }
        const ownProps = {
          location: {},
          match: { params: {} },
          query: { parse: () => ({}) },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toHaveProperty('hasTokenBeenChecked', false)
      })
    })

    describe('isValidToken', () => {
      it('should mark the token status', () => {
        // given
        state = { token: { isValid: true } }
        const ownProps = {
          location: {},
          match: { params: {} },
          query: { parse: () => ({}) },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toHaveProperty('isValidToken', true)
      })
    })
  })
})
