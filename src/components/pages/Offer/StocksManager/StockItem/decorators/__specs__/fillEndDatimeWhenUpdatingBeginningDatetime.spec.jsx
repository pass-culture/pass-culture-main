import { mount } from 'enzyme'
import React from 'react'
import { Field, Form } from 'react-final-form'

import fillEndDatimeWhenUpdatingBeginningDatetime from '../fillEndDatimeWhenUpdatingBeginningDatetime'

describe('src | components | pages | Offer | StockItem | decorators | fillEndDatimeWhenUpdatingBeginningDatetime', () => {
  it('should update the endDateTime date to the beginningDateTime with keeping hours and minute of previous target date, when both dates are already initialized', () => {
    // given
    const dateModified = '2022-08-28T23:37:00.000Z'
    const beginningDateTime = '2019-05-27T10:01:00Z'
    const endDateTime = '2019-06-05T12:02:00Z'
    const endTime = '14:16'

    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
    }
    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
          }),
        ]}
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
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
            <button
              onClick={handleSubmit}
              type="submit"
            >
              {'Submit'}
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
    function handleOnSubmit(formValues) {
      expect(formValues.beginningDateTime).toStrictEqual(dateModified)
      expect(formValues.endDateTime).toStrictEqual('2022-08-28T12:02:00.000Z')
    }
  })

  it('should update the endDateTime to null  when beginningDateTime is null', () => {
    // given
    const beginningDateTime = '2019-09-27T10:01:00Z'
    const endDateTime = '2019-11-01T12:02:00Z'
    const endTime = '14:16'
    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
    }

    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
          }),
        ]}
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
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
            <button
              onClick={handleSubmit}
              type="submit"
            >
              {'Submit'}
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
    function handleOnSubmit(formValues) {
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
    const initialValues = {
      beginningDateTime,
      endDateTime,
      endTime,
    }

    const wrapper = mount(
      <Form
        decorators={[
          fillEndDatimeWhenUpdatingBeginningDatetime({
            triggerDateName: 'beginningDateTime',
            targetDateName: 'endDateTime',
            targetTimeName: 'endTime',
          }),
        ]}
        initialValues={initialValues}
        onSubmit={handleOnSubmit}
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
            <button
              onClick={handleSubmit}
              type="submit"
            >
              {'Submit'}
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
    function handleOnSubmit(formValues) {
      expect(formValues.beginningDateTime).toStrictEqual(dateModified)
      expect(formValues.endDateTime).toStrictEqual(dateModified)
    }
  })
})
