/* eslint-disable no-use-before-define */
import { mount } from 'enzyme'
import 'moment-timezone'
import React from 'react'
import { Field, Form } from 'react-final-form'

import forceDateAtSpecificHoursAndMinutes from '../forceDateAtSpecificHoursAndMinutes'

describe('src | selectors | forceDateAtSpecificHoursAndMinutes', () => {
  it('should force the date to have specific hours and minutes', done => {
    // given
    const initialValues = {
      fooDate: '2019-04-28T19:00:00.000Z',
    }

    // when
    const wrapper = mount(
      <Form
        decorators={[
          forceDateAtSpecificHoursAndMinutes({
            dateName: 'fooDate',
            hours: 23,
            minutes: 59,
          }),
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="fooDate"
              render={({ input }) => <input {...input} />}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // then
    setTimeout(() => {
      wrapper.update()
      const input = wrapper
        .find(Field)
        .find({ name: 'fooDate' })
        .find('input')
      expect(input.props().value).toEqual('2019-04-28T23:59:00.000Z')

      // when
      input.simulate('change', {
        target: { value: '2019-04-28T19:00:00.000Z' },
      })
      setTimeout(() => {
        wrapper.update()
        wrapper.find('button[type="submit"]').simulate('click')
      })
    })

    // then
    function onSubmit(formValues) {
      expect(formValues.fooDate).toEqual('2019-04-28T23:59:00.000Z')
      done()
    }
  })
})
