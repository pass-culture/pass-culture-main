/* eslint-disable no-use-before-define */
import { mount, shallow } from 'enzyme'
import moment from 'moment'
import React from 'react'
import { Form } from 'react-final-form'

import { DateField } from '../DateField'

describe('src | components | layout | form | DateField', () => {
  it('should match snapchot', () => {
    // given
    const initialValues = {
      myDate: '2019-04-27T20:00:00Z',
    }

    // when
    const wrapper = shallow(
      <Form
        initialValues={initialValues}
        onSubmit={() => ({})}
        render={({ handleSubmit }) => (
          <form>
            <DateField name="myDate" />
            <button onClick={handleSubmit} type="submit">
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

  it('should submit a form with a date', done => {
    // given
    const initialValues = {
      myDate: '2019-04-27T20:00:00Z',
    }
    const wrapper = mount(
      <Form
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <DateField name="myDate" />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find(DateField)
      .find('input[name="myDate"]')
      .simulate('click')
    wrapper
      .find('DatePicker')
      .props()
      .onChange(moment('2019-04-28T20:00:00Z'))
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.myDate).toEqual('2019-04-28T20:00:00.000Z')
      done()
    }
  })

  it('should display the date taking in account the timezone', () => {
    // given
    const initialValues = {
      myDate: '2019-04-27T02:00:00Z',
    }

    // when
    const wrapper = mount(
      <Form
        initialValues={initialValues}
        onSubmit={() => null}
        render={({ handleSubmit }) => (
          <form>
            <DateField name="myDate" readOnly timezone="America/Cayenne" />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    expect(
      wrapper
        .find(DateField)
        .find('input[name="myDate"]')
        .props().value
    ).toEqual('26/04/2019')
  })
})
