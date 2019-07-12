import React from 'react'
import { shallow } from 'enzyme'
import { Form } from 'react-final-form'
import { Redirect } from 'react-router'
import { FormFooter } from '../../../../forms/FormFooter'

import RawActivationPassword from '../RawActivationPassword'

describe('src | components | pages | activation | password | RawActivationPassword', () => {
  let props
  let activationData

  beforeEach(() => {
    props = {
      checkTokenIsValid: jest.fn(),
      hasTokenBeenChecked: false,
      history: {
        push: jest.fn(),
        replace: jest.fn(),
      },
      initialValues: {},
      isValidToken: true,
      isValidUrl: true,
      loginUserAfterPasswordSaveSuccess: jest.fn(),
      sendActivationPasswordForm: jest.fn(),
    }

    activationData = {
      cguCheckBox: 'checked',
      email: 'john@example.com',
      newPassword: 'Azertyuiopl18!',
      newPasswordConfirm: 'Azertyuiopl18!',
      token: 'AZERTY123',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<RawActivationPassword {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should mount component with isLoading as false', () => {
    // when
    const wrapper = shallow(<RawActivationPassword {...props} />)

    // then
    expect(wrapper.state().isLoading).toBe(false)
  })

  describe('when token validity has not been checked', () => {
    it('should check token validity', () => {
      // Given
      props.hasTokenBeenChecked = false
      props.initialValues.token = 'my-token-to-check'

      // When
      shallow(<RawActivationPassword {...props} />)

      // then
      expect(props.checkTokenIsValid).toHaveBeenCalledWith('my-token-to-check')
    })

    it('should not redirect to invalid link page when token is marked as invalid', () => {
      // Given
      props.hasTokenBeenChecked = false
      props.isValidToken = false

      // When
      const wrapper = shallow(<RawActivationPassword {...props} />)

      // then
      const redirectComponent = wrapper.find(Redirect)
      expect(redirectComponent).toHaveLength(0)
    })
  })

  describe('when token validity has been checked', () => {
    it('should not check validity', () => {
      // Given
      props.hasTokenBeenChecked = true
      props.initialValues.token = 'my-token-to-check'

      // When
      shallow(<RawActivationPassword {...props} />)

      // then
      expect(props.checkTokenIsValid).not.toHaveBeenCalled()
    })

    describe('when the token is not valid', () => {
      it('should redirect to activation error page', () => {
        // given
        props.hasTokenBeenChecked = true
        props.isValidToken = false

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)

        // then
        const redirectComponent = wrapper.find(Redirect)
        expect(redirectComponent).toHaveLength(1)
        expect(redirectComponent.prop('to')).toBe('/activation/lien-invalide')
      })
    })
  })

  describe('when the isValidUrl is false', () => {
    it('should redirect to activation error page', () => {
      // when
      const wrapper = shallow(<RawActivationPassword
        {...props}
        isValidUrl={false}
                              />)

      // then
      const redirectComponent = wrapper.find(Redirect)
      expect(redirectComponent).toHaveLength(1)
      expect(redirectComponent.prop('to')).toBe('/activation/error')
    })
  })

  describe('when submit activation password form', () => {
    beforeEach(() => {
      props.initialValues = {
        email: 'fake email',
        token: 'fake token',
      }
    })

    it('should prevent submit when information are loading', () => {
      // when
      const wrapper = shallow(<RawActivationPassword {...props} />)
      const form = wrapper.find(Form).dive()
      const formFooter = form.find(FormFooter).dive()

      // then
      expect(formFooter.find('button[type="submit"]').prop('disabled')).toBe(true)
    })

    it('should send password details to api', () => {
      // when
      const wrapper = shallow(<RawActivationPassword {...props} />)
      wrapper.find(Form).prop('onSubmit')(activationData)

      // then
      expect(wrapper.state('isLoading')).toBe(true)
      expect(props.sendActivationPasswordForm).toHaveBeenCalledWith(
        activationData,
        expect.anything(),
        expect.anything()
      )
    })

    describe('when submission failed', () => {
      it('should mark component as not loading', async () => {
        // given
        const formResolver = jest.fn()
        props.sendActivationPasswordForm = (_, fail) =>
          Promise.reject(new Error('Activation failed on API')).catch(() => {
            fail(formResolver)(
              {},
              {
                payload: { errors: [{ code: 1234 }, { code: 5678 }] },
              }
            )
          })

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(wrapper.state('isLoading')).toBe(false)
      })

      it('should report first error found to form when multiple errors are received', async () => {
        // given
        const formResolver = jest.fn()
        props.sendActivationPasswordForm = (values, fail) =>
          Promise.reject(new Error('Activation failed on API')).catch(() => {
            fail(formResolver)(
              {},
              {
                payload: { errors: [{ code: 1234 }, { code: 5678 }] },
              }
            )
          })

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(formResolver).toHaveBeenCalledWith({ code: 1234 })
      })

      it('should report error found to form when single error is received', async () => {
        // given
        const formResolver = jest.fn()
        props.sendActivationPasswordForm = (values, fail) =>
          Promise.reject(new Error('Activation failed on API')).catch(() => {
            fail(formResolver)(
              {},
              {
                payload: { errors: { code: 1234 } },
              }
            )
          })

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(formResolver).toHaveBeenCalledWith({ code: 1234 })
      })
    })

    describe('when submission succeed', () => {
      let formResolver

      beforeEach(() => {
        formResolver = jest.fn()
        props.sendActivationPasswordForm = (_, fail, success) =>
          Promise.resolve().then(() => {
            success(formResolver, activationData)()
          })
      })

      it('should mark component as loading', async () => {
        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(wrapper.state('isLoading')).toStrictEqual(true)
      })

      it('should redirect user to activation/error when failed', async () => {
        // given
        jest
          .spyOn(props, 'loginUserAfterPasswordSaveSuccess')
          .mockImplementation((_, fail) => fail())

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(props.loginUserAfterPasswordSaveSuccess).toHaveBeenCalledTimes(1)
        expect(props.loginUserAfterPasswordSaveSuccess).toHaveBeenCalledWith(
          activationData,
          expect.anything(),
          expect.anything()
        )
        expect(props.history.push).toHaveBeenCalledWith('/activation/error')
      })

      it('should redirect user to /decouverte page when succeed', async () => {
        // given
        props.loginUserAfterPasswordSaveSuccess = (_, fail, success) => success(formResolver)

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(props.history.replace).toHaveBeenCalledWith('/typeform?from=password')
      })
    })
  })
})
