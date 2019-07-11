import { mount, shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import { NumberField } from '../NumberField'

describe('src | components | layout | form | NumberField', () => {
  it('should match snapshot', () => {
    // given
    const initialValues = {
      bar: 3,
      foo: 5.6,
    }

    // when
    const wrapper = shallow(
      <Form
        initialValues={initialValues}
        onSubmit={() => ({})}
        render={({ handleSubmit }) => (
          <form>
            <NumberField name="foo" />
            <NumberField name="bar" />
            <button
              onClick={handleSubmit}
              type="submit"
            >
              Submit
            </button>
          </form>
        )}
      />
    )

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should submit a form with number field when number is a decimal with a dot', () => {return new Promise(done => {
    // given
    const initialValues = {
      bar: '3',
      foo: '5.6',
    }
    const wrapper = mount(
      <Form
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <NumberField name="bar" />
            <NumberField name="foo" />
            <button
              onClick={handleSubmit}
              type="submit"
            >
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find(NumberField)
      .find({ name: 'bar' })
      .find('input')
      .simulate('change', { target: { value: '6' } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.bar).toStrictEqual(6)
      expect(formValues.foo).toStrictEqual(initialValues.foo)
      done()
    }
  })})

  it('should submit a form with number field when number is a decimal with a comma', () => {return new Promise(done => {
    // given
    const initialValues = {
      bar: '3',
      foo: '5,6',
    }
    const wrapper = mount(
      <Form
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <NumberField name="bar" />
            <NumberField name="foo" />
            <button
              onClick={handleSubmit}
              type="submit"
            >
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find(NumberField)
      .find({ name: 'bar' })
      .find('input')
      .simulate('change', { target: { value: '6' } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.bar).toStrictEqual(6)
      expect(formValues.foo).toStrictEqual(initialValues.foo)
      done()
    }
  })})
})
