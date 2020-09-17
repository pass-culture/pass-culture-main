import { mount } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import TimeField from '../TimeField'

describe('src | components | layout | form | TimeField', () => {
  it('should submit a form with a time', async() => {
    await new Promise(done => {
      // given
      const wrapper = mount(
        <Form
          onSubmit={handleOnSubmit}
          render={({ handleSubmit }) => (
            <form>
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
        expect(formValues.myTime).toStrictEqual('03:45')
        done()
      }
    })
  })
})
