import { shallow } from 'enzyme'
import React from 'react'

import FormFooter from '../../../../forms/FormFooter'
import HiddenField from '../../../../forms/inputs/HiddenField'
import PasswordField from '../../../../forms/inputs/PasswordField'
import { ResetPasswordForm } from '../ResetPasswordForm'

describe('src | components | ResetPasswordForm', () => {
  it('should display sentences, two password fields, a hidden field and form footer', () => {
    // given
    const props = { canSubmit: true, isLoading: false }

    // when
    const wrapper = shallow(<ResetPasswordForm {...props} />)

    // then
    const sentence1 = wrapper.find({ children: 'Saisissez ci-dessous' })
    const sentence2 = wrapper.find({ children: 'votre nouveau mot de passe.' })
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
})
