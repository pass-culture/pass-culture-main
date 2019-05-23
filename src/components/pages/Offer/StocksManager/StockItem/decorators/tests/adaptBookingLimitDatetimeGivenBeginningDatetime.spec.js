import { mount } from 'enzyme'
import React from 'react'
import { Field, Form } from 'react-final-form'

import adaptBookingLimitDatetimeGivenBeginningDatetime from '../adaptBookingLimitDatetimeGivenBeginningDatetime'

describe('src | pages | Offer | StocksManager | StockItem | decorators | adaptaBookingLimitDatetimeGivenBeginningDatetime', () => {
  it('should set bookingLimitDatetime at 23h59 plus 3 hours for america/cayenne (because utc)', () => {
    // given
    const initialValues = {
      beginningDatetime: '2019-04-28T19:00:00.000Z',
      bookingLimitDatetime: '2019-04-20T15:00:00.000Z',
    }

    // when
    const wrapper = mount(
      <Form
        decorators={[
          adaptBookingLimitDatetimeGivenBeginningDatetime({
            isEvent: true,
            timezone: 'America/Cayenne',
          }),
        ]}
        initialValues={initialValues}
        onSubmit={() => null}
        render={({ handleSubmit }) => (
          <form>
            <Field
              name="beginningDatetime"
              render={({ input }) => <input {...input} />}
            />
            <Field
              name="bookingLimitDatetime"
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
    const input = wrapper
      .find(Field)
      .find({ name: 'bookingLimitDatetime' })
      .find('input')
    expect(input.props().value).toEqual('2019-04-21T02:59:00.000Z')
  })
})
