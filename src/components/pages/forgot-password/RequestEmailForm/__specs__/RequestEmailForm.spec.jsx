import { shallow, mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import React from 'react'
import { Form } from 'react-final-form'

import { RequestEmailForm } from '../RequestEmailForm'
import InputField from '../../../../forms/inputs/InputField'
import FormFooter from '../../../../forms/FormFooter'

const defaultRequiredProps = {
  hasValidationErrors: false,
  isLoading: false,
  dispatch: jest.fn(),
  history: {},
  location: {},
}

describe('src | components | RequestEmailForm', () => {
  it('should display a sentence, an input text field and form footer', () => {
    // given
    const props = {
      ...defaultRequiredProps,
      canSubmit: true,
      hasSubmitErrors: false,
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

  it('should display the FormError if there are errors on submit', async () => {
    // given
    const props = {
      ...defaultRequiredProps,
      canSubmit: false,
      hasSubmitErrors: true,
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <Form onSubmit={jest.fn()}>
          {() => <RequestEmailForm {...props} />}
        </Form>
      </MemoryRouter>
    )

    // then
    const sentence = await wrapper.find('div.form-error-message').childAt(0)
    expect(sentence.text()).toBe(
      'Un problème est survenu pendant la réinitialisation du mot de passe, réessaie plus tard.'
    )
  })
})
