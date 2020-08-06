import { shallow } from 'enzyme'
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'

import Logo from '../../../layout/Logo'
import LostPassword from '../LostPassword'

describe('src | components | pages | LostPassword', () => {
  let props

  beforeEach(() => {
    props = {
      change: false,
      envoye: false,
      errors: {},
      token: 'ABC',
    }
  })

  it('should display sentences, a form with two fields', () => {
    // when
    const wrapper = shallow(<LostPassword {...props} />)

    // then
    const logo = wrapper.find(Logo)
    const sentence1 = wrapper.find({ children: 'Créer un nouveau mot de passe' })
    const sentence2 = wrapper.find({ children: 'Saisissez le nouveau mot de passe' })
    const form = wrapper.find(Form)
    const field = wrapper.find(Field)
    const submitButton = wrapper.find(SubmitButton)
    expect(logo).toHaveLength(1)
    expect(sentence1).toHaveLength(1)
    expect(sentence2).toHaveLength(1)
    expect(form).toHaveLength(1)
    expect(field).toHaveLength(2)
    expect(submitButton).toHaveLength(1)
  })
})
