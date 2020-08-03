import { shallow } from 'enzyme'
import React from 'react'

import { RequestEmailForm } from '../RequestEmailForm'
import InputField from '../../../../forms/inputs/InputField'
import FormFooter from '../../../../forms/FormFooter'

describe('src | components | RequestEmailForm', () => {
  it('should display a sentence, an input text field and form footer', () => {
    // given
    const props = {
      canSubmit: true,
      isLoading: false,
    }

    // when
    const wrapper = shallow(<RequestEmailForm {...props} />)

    // then
    const sentence = wrapper.find({
      children: 'Renseigne ton adresse e-mail pour réinitialiser ton mot de passe.',
    })
    const input = wrapper.find(InputField)
    const formFooter = wrapper.find(FormFooter)
    expect(sentence).toHaveLength(1)
    expect(input).toHaveLength(1)
    expect(formFooter).toHaveLength(1)
  })
})
