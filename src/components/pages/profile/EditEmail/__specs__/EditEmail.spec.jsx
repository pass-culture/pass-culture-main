import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import EditEmail from '../EditEmail'
import { act } from 'react-dom/test-utils'
import { updateEmail } from '../../repository/updateEmail'
import { toast } from 'react-toastify'

jest.mock('../../repository/updateEmail', () => {
  return {
    updateEmail: jest.fn(),
  }
})

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

let _fillFormWithValidInputs = function (props, { new_email, password }) {
  const wrapper = mount(
    <MemoryRouter>
      <EditEmail {...props} />
    </MemoryRouter>
  )
  const newEmailInput = wrapper.find('input[name="new-email"]')
  const passwordInput = wrapper.find('input[name="password"]')

  act(() => {
    newEmailInput.invoke('onChange')({ target: { value: new_email } })
    passwordInput.invoke('onChange')({ target: { value: password } })
  })
  wrapper.update()

  return wrapper
}

describe('change email page', () => {
  let props
  beforeEach(() => {
    jest.resetAllMocks()

    props = {
      redirectToPersonnalInformationPage: jest.fn(),
    }
  })

  describe('when filling the email field', () => {
    it('should prevent email submission when email is invalid', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EditEmail {...props} />
        </MemoryRouter>
      )
      const newEmailInput = wrapper.find('input[name="new-email"]')

      // when
      act(() => {
        newEmailInput.invoke('onChange')({ target: { value: 'wrongemail.com' } })
      })
      wrapper.update()

      // then
      const submitButton = wrapper.find('form').find('input[type="submit"]')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('disabled')).toBe(true)
    })

    it('should display an error message when email is invalid', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EditEmail {...props} />
        </MemoryRouter>
      )
      const newEmailInput = wrapper.find('input[name="new-email"]')

      // when
      act(() => {
        newEmailInput.invoke('onChange')({ target: { value: 'wrongemail.com' } })
      })
      wrapper.update()

      // then
      const emailField = wrapper.find('form').find('input[name="new-email"]').closest('.pf-field')
      const emailErrorLabel = emailField.find('.pf-field-error')

      expect(emailErrorLabel).toHaveLength(1)
      expect(emailErrorLabel.text()).toContain("Format de l'e-mail incorrect")
    })

    it('should hide error message when email get valid', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EditEmail {...props} />
        </MemoryRouter>
      )
      const newEmailInput = wrapper.find('input[name="new-email"]')

      // when
      act(() => {
        newEmailInput.invoke('onChange')({ target: { value: 'wrongemail.com' } })
        newEmailInput.invoke('onChange')({ target: { value: 'fixed@example.com' } })
      })
      wrapper.update()

      // then
      const emailField = wrapper.find('form').find('input[name="new-email"]').closest('.pf-field')
      const emailErrorLabel = emailField.find('.pf-field-error')

      expect(emailErrorLabel).toHaveLength(0)
    })

    it('should prevent email submission when no email given', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EditEmail {...props} />
        </MemoryRouter>
      )

      // then
      const submitButton = wrapper.find('form').find('input[type="submit"]')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('disabled')).toBe(true)
    })
  })

  it('should prevent form submission when no password given', () => {
    // given
    const wrapper = mount(
      <MemoryRouter>
        <EditEmail {...props} />
      </MemoryRouter>
    )
    const newEmailInput = wrapper.find('input[name="new-email"]')

    // when
    act(() => {
      newEmailInput.invoke('onChange')({ target: { value: 'email@example.com' } })
    })
    wrapper.update()

    // then
    const submitButton = wrapper.find('form').find('input[type="submit"]')
    expect(submitButton).toHaveLength(1)
    expect(submitButton.prop('disabled')).toBe(true)
  })

  it('should allow submission when email and password are given', () => {
    // given
    const wrapper = mount(
      <MemoryRouter>
        <EditEmail {...props} />
      </MemoryRouter>
    )
    const newEmailInput = wrapper.find('input[name="new-email"]')
    const password = wrapper.find('input[name="password"]')

    // when
    act(() => {
      newEmailInput.invoke('onChange')({ target: { value: 'email@example.net' } })
      password.invoke('onChange')({ target: { value: '123456789' } })
    })
    wrapper.update()

    // then
    const submitButton = wrapper.find('form').find('input[type="submit"]')
    expect(submitButton).toHaveLength(1)
    expect(submitButton.prop('disabled')).toBe(false)
  })

  describe('when sending the form', () => {
    let submitForm = function (emailFormButton, wrapper) {
      return act(async () => {
        await emailFormButton.invoke('onSubmit')({
          preventDefault: jest.fn(),
        })
        wrapper.update()
      })
    }

    it('should send the new email with current password', async () => {
      // given
      updateEmail.mockResolvedValueOnce({ status: 204 })
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'toto123',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      expect(updateEmail).toHaveBeenCalledTimes(1)
      expect(updateEmail).toHaveBeenCalledWith({
        new_email: 'test@example.net',
        password: 'toto123',
      })
    })

    it('should display a success notification when the change is a success', async () => {
      // given
      updateEmail.mockResolvedValueOnce({ status: 204 })
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'toto123',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      await expect(toast.success).toHaveBeenCalledTimes(1)
      expect(toast.success).toHaveBeenCalledWith('L’e-mail a bien été envoyé.')
    })

    it('should display an error notification when updating email has failed', async () => {
      // given
      updateEmail.mockRejectedValueOnce()
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'toto123',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      expect(toast.error).toHaveBeenCalledTimes(1)
      expect(toast.error).toHaveBeenCalledWith('La modification de l’adresse e-mail a échouée.')
    })

    it('should display a field error when api return an error for password', async () => {
      // given
      updateEmail.mockResolvedValueOnce({
        status: 401,
        json: () =>
          Promise.resolve({
            password: ['Mot de passe incorrect'],
          }),
      })
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'wrongPassword',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      const passwordField = wrapper.find('form').find('input[type="password"]').closest('.pf-field')
      const passwordErrorLabel = passwordField.find('.pf-field-error')
      expect(passwordErrorLabel).toHaveLength(1)
      expect(passwordErrorLabel.text()).toContain('Mot de passe incorrect')
    })

    it('should hide errors when second call is a success', async () => {
      // given
      updateEmail.mockResolvedValueOnce({
        status: 401,
        json: () =>
          Promise.resolve({
            password: ['Mot de passe incorrect'],
          }),
      })

      updateEmail.mockResolvedValueOnce({
        status: 204,
      })
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'wrongPassword',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)
      await submitForm(emailFormButton, wrapper)

      // then
      const passwordField = wrapper.find('form').find('input[type="password"]').closest('.pf-field')
      const passwordErrorLabel = passwordField.find('.pf-field-error')
      expect(passwordErrorLabel).toHaveLength(0)
    })

    it('should redirect to personnal information on success', async () => {
      // given
      updateEmail.mockResolvedValueOnce({
        status: 204,
      })
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'wrongPassword',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      expect(props.redirectToPersonnalInformationPage).toHaveBeenCalledTimes(1)
    })

    it('should not redirect anywhere when the form is in error', async () => {
      // given
      updateEmail.mockRejectedValueOnce()
      const wrapper = _fillFormWithValidInputs(props, {
        new_email: 'test@example.net',
        password: 'toto123',
      })

      // when
      const emailFormButton = wrapper.find('form')
      await submitForm(emailFormButton, wrapper)

      // then
      expect(props.redirectToPersonnalInformationPage).toHaveBeenCalledTimes(0)
    })
  })
})
