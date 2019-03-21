import React from 'react'
import { mount, shallow } from 'enzyme'
import { Form } from 'react-final-form'
import { FormFooter } from '../../../../forms/FormFooter'
import FormInputs from '../inputs'

import RawActivationPassword from '../RawActivationPassword'

describe('src | components | pages | activation | password | RawActivationPassword', () => {
  let props
  let activationData

  beforeEach(() => {
    props = {
      history: {
        push: jest.fn(),
        replace: jest.fn(),
      },
      initialValues: {},
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
      expect(formFooter.find('button[type="submit"]').prop('disabled')).toBe(
        true
      )
    })

    it.skip('should authorize submit when information are valid', () => {
      // given
      const wrapper = mount(<RawActivationPassword {...props} />)
      const form = wrapper.find(Form)
      const formInputs = form.find(FormInputs)

      // when
      const passwordFields = formInputs.find('PasswordField')
      passwordFields
        .at(0)
        .find('input[name="newPassword"]')
        .simulate('change', { target: { value: 'Azerty123456789#' } })
      passwordFields
        .at(1)
        .find('input[name="newPasswordConfirm"]')
        .simulate('change', { target: { value: 'Azerty123456789#' } })
      const checkboxField = formInputs.find('CheckBoxField')
      checkboxField
        .find('input[type="checkbox"]')
        .simulate('change', { target: { value: true } })

      const formFooter = wrapper.find(Form).find(FormFooter)
      const submitButton = formFooter.find('button[type="submit"]')
      submitButton.html().click()

      // then
      expect(props.sendActivationPasswordForm).toHaveBeenCalled()
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
        expect(wrapper.state('isLoading')).toEqual(true)
      })

      it('should redirect user to activation/error when failed', async () => {
        // given
        props.loginUserAfterPasswordSaveSuccess = jest.fn((_, fail) => fail())

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
        props.loginUserAfterPasswordSaveSuccess = (_, fail, success) =>
          success(formResolver)

        // when
        const wrapper = shallow(<RawActivationPassword {...props} />)
        await wrapper.find(Form).prop('onSubmit')(activationData)

        // then
        expect(props.history.replace).toHaveBeenCalledWith(
          '/decouverte?from=password'
        )
      })
    })
  })
})
