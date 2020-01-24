/* eslint-disable no-use-before-define */
import { mount } from 'enzyme'
import 'moment-timezone'
import React from 'react'
import { Field, Form } from 'react-final-form'

import { bindTimeFieldWithDateField } from '../bindTimeFieldWithDateField'

describe('src | selectors | bindTimeFieldWithDateField', () => {
  it('should update the date when time is updated', done => {
    // given
    const initialValues = {
      dateTime: "2019-04-27T19:00:00Z"
    }
    const wrapper = mount(
      <Form
        decorators={[
          bindTimeFieldWithDateField({
            dateName: 'dateTime',
            timeName: 'time',
          })
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="dateTime"
              render={({ input }) => (
                <input {...input} />
              )}
            />
            <Field
              name="time"
              render={({ input }) => (
                <input {...input} />
              )}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper.find(Field)
      .find({ name: "time" })
      .find("input")
      .simulate("change", { target: { value: "16:00" } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.dateTime).toEqual("2019-04-27T16:00:00.000Z")
      expect(formValues.time).toEqual("16:00")
      done()
    }
  })


  it('should clamp the time of the date to the defined time', done => {
    // given
    const initialValues = {
      dateTime: "2019-04-27T19:00:00Z"
    }
    const wrapper = mount(
      <Form
        decorators={[
          bindTimeFieldWithDateField({
            dateName: 'dateTime',
            timeName: 'time',
          })
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="dateTime"
              render={({ input }) => (
                <input {...input} />
              )}
            />
            <Field
              name="time"
              render={({ input }) => (
                <input {...input} />
              )}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper.find(Field)
      .find({ name: "dateTime" })
      .find("input")
      .simulate("change", { target: { value: "2019-04-28T20:00:00Z" } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.dateTime).toEqual("2019-04-28T19:00:00.000Z")
      expect(formValues.time).toEqual("19:00")
      done()
    }
  })

})
