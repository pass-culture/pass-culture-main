import { shallow, mount } from 'enzyme'
import { FORM_ERROR } from 'final-form'
import { MemoryRouter } from 'react-router'
import React from 'react'
import { Form } from 'react-final-form'

import FormFooter from '../../../../forms/FormFooter'
import HiddenField from '../../../../forms/inputs/HiddenField'
import PasswordField from '../../../../forms/inputs/PasswordField'
import { ResetPasswordForm } from '../ResetPasswordForm'

const defaultRequiredProps = {
  hasValidationErrors: false,
  isLoading: false,
  dispatch: jest.fn(),
  history: {},
  location: {},
  hasSubmitErrors: false,
}

describe('src | components | ResetPasswordForm', () => {
  it('should display sentences, two password fields, a hidden field and form footer', () => {
    // given
    const props = { ...defaultRequiredProps, canSubmit: true, isLoading: false }

    // when
    const wrapper = shallow(<ResetPasswordForm {...props} />)

    // then
    const sentence1 = wrapper.find({ children: 'Saisis ci-dessous' })
    const sentence2 = wrapper.find({ children: 'ton nouveau mot de passe.' })
    const sentence3 = wrapper.find({
      children:
        'Il doit contenir au minimum 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.',
    })
    const passwordField = wrapper.find(PasswordField)
    const hiddenField = wrapper.find(HiddenField)
    const formFooter = wrapper.find(FormFooter)
    expect(sentence1).toHaveLength(1)
    expect(sentence2).toHaveLength(1)
    expect(sentence3).toHaveLength(1)
    expect(passwordField).toHaveLength(2)
    expect(hiddenField).toHaveLength(1)
    expect(formFooter).toHaveLength(1)
  })

  it('should display the FormError if there are errors on validate', async () => {
    // given
    const props = {
      ...defaultRequiredProps,
      canSubmit: false,
      hasValidationErrors: true,
      validationErrors: {
        [FORM_ERROR]: 'Les mots de passe ne sont pas les mêmes.',
      },
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <Form onSubmit={jest.fn()}>
          {() => <ResetPasswordForm {...props} />}
        </Form>
      </MemoryRouter>
    )

    // then
    const sentence = await wrapper.find('div.form-error-message').childAt(0)
    expect(sentence.text()).toBe('Les mots de passe ne sont pas les mêmes.')
  })
})
