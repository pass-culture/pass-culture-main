import { mount } from 'enzyme'
import 'moment-timezone'
import React from 'react'
import { Field, Form } from 'react-final-form'
import 
  fillEndDatimeWhenUpdatingBeginningDatetime 
from '../fillEndDatimeWhenUpdatingBeginningDatetime'


describe('src | components | pages | Offer | StockItem | fillEndDatimeWhenUpdatingBeginningDatetime', () => {
  it('should update the target date to the trigger one with keeping hours and minute of previous target date, when both dates are already initialized', done => {
    // given
    const initialValues = {}
    const beginningDateTime = "2019-04-27T19:00:00Z"
    const endDateTime = "2019-04-27T20:00:00Z"
    const endTime = null
    const timezone = "Europe/Paris"


    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            'beginningDatetime',
            'endDatetime',
            'endTime',
            timezone
          })
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="beginningDateTime"
              render={({ input }) => (
                <input {...input} />
              )}
            />
            <Field
              name="endDateTime"
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
           .find({ name: "beginningDateTime" })
           .find("input")
           .simulate("change", { target: { value: "2019-04-28T19:00:00.000Z" } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.beginningDateTime).toEqual("2019-04-28T19:00:00.000Z")
      expect(formValues.endDateTime).toEqual("2019-04-28T20:00:00.000Z")
      done()
    }
  })
})
