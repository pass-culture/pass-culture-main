import { mount } from 'enzyme'
import moment from 'moment'
import React from 'react'
import { Form } from 'react-final-form'

import DateField from '../DateField'

describe('src | components | layout | form | DateField', () => {
  it('should submit a form with a date', () => {
    return new Promise(done => {
      // given
      const initialValues = {
        myDate: '2019-04-27T20:00:00Z',
      }
      const wrapper = mount(
        <Form
          initialValues={initialValues}
          onSubmit={handleOnSubmit}
          render={({ handleSubmit }) => (
            <form>
              <DateField name="myDate" />
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
        .find(DateField)
        .find('input[name="myDate"]')
        .simulate('click')
      wrapper
        .find('DatePicker')
        .props()
        .onChange(moment('2019-04-28T20:00:00Z'))
      wrapper.find('button[type="submit"]').simulate('click')

      // then
      function handleOnSubmit(formValues) {
        expect(formValues.myDate).toStrictEqual('2019-04-28T20:00:00.000Z')
        done()
      }
    })
  })

  it('should display the date taking into account the timezone', () => {
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
            <DateField
              name="myDate"
              readOnly
              timezone="America/Cayenne"
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
    expect(
      wrapper
        .find(DateField)
        .find('input[name="myDate"]')
        .props().value
    ).toStrictEqual('26/04/2019')
  })

  it('should delete date when delete is pressed', () => {
    return new Promise(done => {
      // given
      const initialValues = {
        myDate: '2019-04-27T20:00:00Z',
      }
      const wrapper = mount(
        <Form
          initialValues={initialValues}
          onSubmit={handleOnSubmit}
          render={({ handleSubmit }) => (
            <form>
              <DateField name="myDate" />
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
        .find(DateField)
        .find('input[name="myDate"]')
        .simulate('click')
        .simulate('keyDown', { keyCode: 8 })
      wrapper.find('button[type="submit"]').simulate('click')

      // then
      function handleOnSubmit(formValues) {
        expect(formValues.myDate).toBeNull()
        done()
      }
    })
  })
})
