import { mount } from 'enzyme'
import React from 'react'

import FilterByBookingStatus from '../FilterByBookingStatus'

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
          booking_status_history: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
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
          booking_status_history: [
            {
              status: 'booked',
              date: '2020-04-03T12:00:00Z',
            },
          ],
        },
      ],
      bookingStatuses: [],
      updateGlobalFilters: jest.fn(),
    }
  })

  it('should display a black filter icon', () => {
    // when
    const wrapper = mount(<FilterByBookingStatus {...props} />)

    // then
    const filterIcon = wrapper.find('img')
    expect(filterIcon.prop('src')).toContain('ico-filter-status-black.svg')
    expect(filterIcon.prop('alt')).toBe('Filtrer par statut')
  })

  it('should not display status filters', () => {
    // when
    const wrapper = mount(<FilterByBookingStatus {...props} />)

    // then
    const checkbox = wrapper.find('input')
    const label = wrapper.find('label')
    expect(checkbox).toHaveLength(0)
    expect(label).toHaveLength(0)
  })

  describe('on focus on the filter icon', () => {
    it('should display a red filter icon', () => {
      // given
      const wrapper = mount(<FilterByBookingStatus {...props} />)

      // when
      wrapper.find('button').simulate('focus')

      // then
      const filterIcon = wrapper.find('img')
      expect(filterIcon.prop('src')).toContain('ico-filter-status-red.svg')
      expect(filterIcon.prop('alt')).toBe('Filtrer par statut')
    })

    it('should show filters with all available status in data', () => {
      // given
      const wrapper = mount(<FilterByBookingStatus {...props} />)
      const filterIcon = wrapper.find('img')

      // when
      filterIcon.simulate('focus')

      // then
      const checkbox = wrapper.find('input')
      const label = wrapper.find('label')
      expect(checkbox).toHaveLength(2)
      expect(checkbox.at(0).props()).toStrictEqual({
        checked: true,
        id: 'bs-booked',
        name: 'booked',
        onChange: expect.any(Function),
        type: 'checkbox',
      })
      expect(checkbox.at(1).props()).toStrictEqual({
        checked: true,
        id: 'bs-validated',
        name: 'validated',
        onChange: expect.any(Function),
        type: 'checkbox',
      })
      expect(label).toHaveLength(2)
      expect(label.at(0).text()).toBe('réservé')
      expect(label.at(1).text()).toBe('validé')
    })

    it('should not hide filters on click on a checkbox', () => {
      // given
      const wrapper = mount(<FilterByBookingStatus {...props} />)
      const filterIcon = wrapper.find('img')
      filterIcon.simulate('focus')

      const checkbox = wrapper.find('input').at(0)

      // when
      checkbox.simulate('mouseDown')
      filterIcon.simulate('blur')
      checkbox.simulate('mouseUp')

      // then
      const label = wrapper.find('label')
      expect(label).toHaveLength(2)
    })

    it('should add value to filters when unchecking on a checkbox', () => {
      // given
      const wrapper = mount(<FilterByBookingStatus {...props} />)
      wrapper.find('img').simulate('focus')

      const checkbox = wrapper.find('input').at(0)

      // when
      checkbox.simulate('change', {
        target: { name: 'validated', checked: false },
      })

      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated'],
      })
    })

    it('should remove value from filters when checking the checkbox', () => {
      // given
      const propsWithInitialFilter = {
        ...props,
        bookingStatuses: ['validated'],
      }
      const wrapper = mount(
        <FilterByBookingStatus {...propsWithInitialFilter} />
      )
      wrapper.find('img').simulate('focus')

      const checkbox = wrapper.find('input').at(0)

      // when
      checkbox.simulate('change', {
        target: { name: 'validated', checked: true },
      })

      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: [],
      })
    })

    it('should add value to already filtered booking status when clicking on a checkbox', () => {
      // given
      const wrapper = mount(<FilterByBookingStatus {...props} />)
      wrapper.find('img').simulate('focus')

      const validatedStatusCheckbox = wrapper.find('input').at(0)
      validatedStatusCheckbox.simulate('change', {
        target: { name: 'validated', checked: false },
      })
      const bookedStatusCheckbox = wrapper.find('input').at(1)

      // when
      bookedStatusCheckbox.simulate('change', {
        target: { name: 'booked', checked: false },
      })

      // then
      expect(props.updateGlobalFilters).toHaveBeenCalledWith({
        bookingStatus: ['validated', 'booked'],
      })
    })
  })
})
