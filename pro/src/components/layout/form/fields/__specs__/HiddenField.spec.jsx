import { mount } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import HiddenField from '../HiddenField'
import TextField from '../TextField'

describe('src | components | layout | form | HiddenField', () => {
  it('should submit a form with a title text field', async () => {
    await new Promise(done => {
      // given
      const initialValues = {
        subtitle: 'Mais jamais sans mon cadis.',
        title: 'J’irai droit au Conforama',
      }
      const wrapper = mount(
        <Form
          initialValues={initialValues}
          onSubmit={handleOnSubmit}
          render={({ handleSubmit }) => (
            <form>
              <TextField name="title" />
              <HiddenField name="subtitle" />
              <button onClick={handleSubmit} type="submit">
                Submit
              </button>
            </form>
          )}
        />
      )

      // when
      wrapper
        .find(TextField)
        .find({ name: 'title' })
        .find('input')
        .simulate('change', { target: { value: 'J’irai droit au But' } })
      wrapper.find('button[type="submit"]').simulate('click')

      // then
      function handleOnSubmit(formValues) {
        expect(formValues.title).toBe('J’irai droit au But')
        expect(formValues.subtitle).toStrictEqual(initialValues.subtitle)
        done()
      }
    })
  })
})
