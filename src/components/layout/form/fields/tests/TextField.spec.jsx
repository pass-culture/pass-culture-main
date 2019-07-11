/* eslint-disable no-use-before-define */
import { mount, shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import { TextField } from '../TextField'

describe('src | components | layout | form | TextField', () => {
  it('should match snapchot', () => {
    // given
    const initialValues = {
      text: 'Ca parle de canapés.',
      title: "J'irai droit au Conforama",
    }

    // when
    const wrapper = shallow(
      <Form
        initialValues={initialValues}
        onSubmit={() => ({})}
        render={({ handleSubmit }) => (
          <form>
            <TextField name="title" />
            <TextField name="text" />
            <button
              onClick={handleSubmit}
              type="submit"
            >
              {"Submit"}
            </button>
          </form>
        )}
      />
    )

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should submit a form with a title text field', () => {return new Promise(done => {
    // given
    const initialValues = {
      text: 'Ca parle de canapés.',
      title: "J'irai droit au Conforama",
    }
    const wrapper = mount(
      <Form
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <TextField name="title" />
            <TextField name="text" />
            <button
              onClick={handleSubmit}
              type="submit"
            >
              {"Submit"}
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
      .simulate('change', { target: { value: "J'irai droit au But" } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.title).toStrictEqual("J'irai droit au But")
      expect(formValues.text).toStrictEqual(initialValues.text)
      done()
    }
  })})
})
