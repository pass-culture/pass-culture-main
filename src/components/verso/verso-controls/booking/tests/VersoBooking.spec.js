// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/booking/tests/VersoBooking.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'
import { RawVersoBookingButton } from '../VersoBooking'

import CancelButton from '../CancelButton'
import BookThisButton from '../BookThisButtonContainer'
import Finishable from '../../../../layout/Finishable'

describe('src | components | verso | verso-controls | booking | RawVersoBookingButton', () => {
  it('should component with bookable features', () => {
    // given
    const props = { booking: null, isFinished: false }
    // when
    const wrapper = shallow(<RawVersoBookingButton {...props} />)
    const cancel = wrapper.find(CancelButton)
    const finishable = wrapper.find(Finishable)
    const bookthis = wrapper.find(BookThisButton)
    // then
    expect(cancel).toHaveLength(0)
    expect(bookthis).toHaveLength(1)
    expect(finishable).toHaveLength(1)
  })
  it('should component with booked/cancellable features', () => {
    // given
    const props = { booking: {}, isFinished: false }
    // when
    const wrapper = shallow(<RawVersoBookingButton {...props} />)
    const cancel = wrapper.find(CancelButton)
    const finishable = wrapper.find(Finishable)
    const bookthis = wrapper.find(BookThisButton)
    // then
    expect(cancel).toHaveLength(1)
    expect(bookthis).toHaveLength(0)
    expect(finishable).toHaveLength(1)
  })
})
