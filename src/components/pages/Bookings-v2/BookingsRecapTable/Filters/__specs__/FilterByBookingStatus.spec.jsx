import React from 'react'
import FilterByBookingStatus from '../FilterByBookingStatus'
import { shallow } from 'enzyme'

describe('components | FilterByBookingStatus', () => {
  let props
  beforeEach(() => {
    props = {
      bookingsRecap: [
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
            type: 'thing',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'booked',
          booking_is_duo: false,
          venue_identifier: 'AE',
        },
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
            type: 'thing',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
          booking_status: 'validated',
          booking_is_duo: true,
          venue_identifier: 'AF',
        },
      ],
      updateGlobalFilters: jest.fn(),
    }
  })

  it('should return filters with all available status in data', () => {
    // when
    const wrapper = shallow(<FilterByBookingStatus {...props} />)

    // then
    const checkbox = wrapper.find('input')
    const label = wrapper.find('label')
    expect(checkbox).toHaveLength(2)
    expect(checkbox.at(0).props()).toStrictEqual({
      defaultChecked: true,
      id: 'bs-booked',
      name: 'booked',
      onChange: expect.any(Function),
      type: 'checkbox',
    })
    expect(checkbox.at(1).props()).toStrictEqual({
      defaultChecked: true,
      id: 'bs-validated',
      name: 'validated',
      onChange: expect.any(Function),
      type: 'checkbox',
    })
    expect(label).toHaveLength(2)
    expect(label.at(0).text()).toBe('booked')
    expect(label.at(1).text()).toBe('validated')
  })

  it('should add value to filters when unchecking on a checkbox', () => {
    // given
    const wrapper = shallow(<FilterByBookingStatus {...props} />)
    const checkbox = wrapper.find('input').at(0)

    // when
    checkbox.simulate('change', { target: { name: 'validated', checked: false } })

    // then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingStatus: ['validated'],
    })
  })

  it('should remove value from filters when checking the checkbox', () => {
    // given
    const wrapper = shallow(<FilterByBookingStatus {...props} />)
    const checkbox = wrapper.find('input').at(0)

    // when
    checkbox.simulate('change', { target: { name: 'validated', checked: true } })

    // then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingStatus: [],
    })
  })

  it('should add value to already filtered booking status when clicking on a checkbox', () => {
    // given
    const wrapper = shallow(<FilterByBookingStatus {...props} />)
    const validatedStatusCheckbox = wrapper.find('input').at(0)
    validatedStatusCheckbox.simulate('change', { target: { name: 'validated', checked: false } })
    const bookedStatusCheckbox = wrapper.find('input').at(1)

    // when
    bookedStatusCheckbox.simulate('change', { target: { name: 'booked', checked: false } })

    // then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingStatus: ['validated', 'booked'],
    })
  })
})
