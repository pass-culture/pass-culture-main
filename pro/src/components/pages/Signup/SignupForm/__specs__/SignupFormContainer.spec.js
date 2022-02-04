import { showNotification } from 'store/reducers/notificationReducer'

import { mapDispatchToProps } from '../SignupFormContainer'

describe('src | components | pages | Signup | SignupFormContainer', () => {
  describe('mapDispatchToProps', () => {
    let dispatch
    let props

    beforeEach(() => {
      dispatch = jest.fn()
      props = {
        history: {
          replace: jest.fn(),
        },
      }
    })

    it('should return an object containing functions to pass to component', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        createNewProUser: expect.any(Function),
        redirectToConfirmation: expect.any(Function),
        notifyError: expect.any(Function),
      })
    })

    describe('createNewProUser', () => {
      it('should create a new user using API', () => {
        // given
        const payload = {
          lastName: 'Lastname',
          firstName: 'Firstname',
          phoneNumber: '0666666666',
          password: 'P@ssw0rd',
          email: 'Firstname@test.test',
          siren: '123456789',
          name: 'GAUMONT',
          address: '999 Rue des tests',
          postalCode: '92200',
          city: 'Ville de test',
          cgu_ok: true,
          contactOk: true,
        }
        const expectedFetchPayload = {
          ...payload,
          publicName: payload.firstName,
        }
        const onHandleFail = jest.fn()
        const onHandleSuccess = jest.fn()
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.createNewProUser(payload, onHandleFail, onHandleSuccess)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/users/signup/pro',
            body: expectedFetchPayload,
            handleFail: onHandleFail,
            handleSuccess: onHandleSuccess,
            method: 'POST',
            name: 'user',
          },
          type: 'REQUEST_DATA_POST_/USERS/SIGNUP/PRO',
        })
      })

      it('should insert publicName value equal to firstName', () => {
        // given
        const payload = {
          lastName: 'Lastname',
          firstName: 'Firstname',
        }
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.createNewProUser(payload, jest.fn(), jest.fn())

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/users/signup/pro',
            body: {
              lastName: 'Lastname',
              firstName: 'Firstname',
              publicName: 'Firstname',
            },
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'POST',
            name: 'user',
          },
          type: 'REQUEST_DATA_POST_/USERS/SIGNUP/PRO',
        })
      })

      it('should remove whistespaces from siren', () => {
        // given
        const payload = {
          siren: '123 456 789',
        }
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.createNewProUser(payload, jest.fn(), jest.fn())

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/users/signup/pro',
            body: {
              siren: '123456789',
            },
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'POST',
            name: 'user',
          },
          type: 'REQUEST_DATA_POST_/USERS/SIGNUP/PRO',
        })
      })
    })

    describe('redirectToConfirmation', () => {
      it('should redirect to confirmation page', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)

        // when
        functions.redirectToConfirmation()

        // then
        expect(props.history.replace).toHaveBeenCalledWith(
          '/inscription/confirmation'
        )
      })
    })

    describe('showNotification', () => {
      it('should display a notification', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)
        const messageText = 'message text'

        // when
        functions.notifyError(messageText)

        // then
        expect(dispatch).toHaveBeenCalledWith(
          showNotification({
            text: messageText,
            type: 'error',
          })
        )
      })
    })
  })
})
