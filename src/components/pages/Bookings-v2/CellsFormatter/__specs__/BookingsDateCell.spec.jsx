import {shallow} from "enzyme/build"
import React from "react"
import BookingDateCell from "../BookingsDateCell"

describe('components | pages | bookings-v2 | CellsFormatter | BookingsDateCell', () => {
  it('should render a div with two span, one containing the date and the other one the time', () => {
    // Given
    const props = {
      'values': {
        'bookingDateInfo': '2020-04-03T12:00:00Z',
      },
    }

    // When
    const wrapper = shallow(<BookingDateCell {...props} />)

    const spans = wrapper.find('span')
    const bookingDateDaySpan = spans.find('span').at(0)
    const bookingDateHourSpan = spans.find('span').at(1)

    // Then
    expect(spans).toHaveLength(2)
    expect(bookingDateDaySpan.text()).toBe('03/04/2020')
    expect(bookingDateHourSpan.text()).toBe('12:00')
  })
})
