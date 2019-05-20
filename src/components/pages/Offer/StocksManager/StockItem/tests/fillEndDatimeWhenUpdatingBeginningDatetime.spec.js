import { mount } from 'enzyme'
import 'moment-timezone'
import React from 'react'
import { Field, Form } from 'react-final-form'
import fillEndDatimeWhenUpdatingBeginningDatetime from '../fillEndDatimeWhenUpdatingBeginningDatetime'

describe('src | components | pages | Offer | StockItem | fillEndDatimeWhenUpdatingBeginningDatetime', () => {
  it('should update the endDateTime date to the beginningDateTime with keeping hours and minute of previous target date, when both dates are already initialized', () => {
    // given
    const dateModified = '2022-04-28T13:37:00.000Z'
    const beginningDateTime = '2019-09-27T10:01:00Z'
    const endDateTime = '2019-11-01T12:02:00Z'
    const endTime = '14:16'
    const timezone = 'Europe/Paris'

    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
      timezone,
    }
    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
            timezone,
          }),
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="beginningDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endTime"
              render={({ input }) => <input {...input} />}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )
    // when
    wrapper
      .find(Field)
      .find({ name: 'beginningDateTime' })
      .find('input')
      .simulate('change', { target: { value: dateModified } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.beginningDateTime).toEqual(dateModified)
      expect(formValues.endDateTime).toEqual('2022-04-28T12:02:00.000Z')
    }
  })

  it('should update the endDateTime to null ? when beginningDateTime is null', () => {
    // given
    const dateModified = '2022-04-28T13:37:00.000Z'
    const beginningDateTime = '2019-09-27T10:01:00Z'
    const endDateTime = '2019-11-01T12:02:00Z'
    const endTime = '14:16'
    const timezone = 'Europe/Paris'
    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
      timezone,
    }

    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
            timezone,
          }),
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="beginningDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endTime"
              render={({ input }) => <input {...input} />}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find({ name: 'beginningDateTime' })
      .find('input')
      .simulate('change', { target: { value: null } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.endDateTime).toBeNull()
      expect(formValues.beginningDateTime).toBeNull()
    }
  })

  it('should update the endDateTime to the beginningDateTime even after beginningDateTime was null', () => {
    // given
    const dateModified = '2022-04-28T13:37:00.000Z'
    const beginningDateTime = '2019-09-27T10:01:00Z'
    const endDateTime = '2019-11-01T12:02:00Z'
    const endTime = '14:16'
    const timezone = 'Europe/Paris'
    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
      timezone,
    }

    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
            timezone,
          }),
        ]}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="beginningDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endDateTime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="endTime"
              render={({ input }) => <input {...input} />}
            />
            <button onClick={handleSubmit} type="submit">
              Submit
            </button>
          </form>
        )}
      />
    )

    // when
    wrapper
      .find({ name: 'beginningDateTime' })
      .find('input')
      .simulate('change', { target: { value: null } })

    wrapper.update()

    wrapper
      .find(Field)
      .find({ name: 'beginningDateTime' })
      .find('input')
      .simulate('change', { target: { value: dateModified } })
    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function onSubmit(formValues) {
      expect(formValues.beginningDateTime).toEqual(dateModified)
      expect(formValues.endDateTime).toEqual(dateModified)
    }
  })
})
