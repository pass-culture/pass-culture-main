import { mount, shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import DateField from '../DateField/DateField'
import TimeField from '../TimeField'

describe('src | components | layout | form | TimeField', () => {
  it('should match the snapchot', () => {
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
            <TimeField name="myTime" />
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

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should submit a form with a time', () => {
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
              <TimeField name="myTime" />
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
        .find(TimeField)
        .find('input[name="myTime"]')
        .simulate('change', { target: { value: '03:45' } })
      wrapper.find('button[type="submit"]').simulate('click')

      // then
      function handleOnSubmit(formValues) {
        expect(formValues.myDate).toStrictEqual('2019-04-27T20:00:00Z')
        expect(formValues.myTime).toStrictEqual('03:45')
        done()
      }
    })
  })
})
