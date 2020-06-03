import { shallow } from 'enzyme'
import React from 'react'

import MyBookingsLists from '../MyBookingsLists'

describe('src | components | pages | my-bookings | MyBookingsLists', () => {
  let props

  beforeEach(() => {
    props = {
      finishedAndUsedAndCancelledBookings: [],
      upComingBookings: [],
      bookingsOfTheWeek: [],
    }
  })

  it('should display the title "Réservations"', () => {
    // When
    const wrapper = shallow(<MyBookingsLists {...props} />)

    // Then
    const title = wrapper.find('h1').find({ children: 'Réservations' })
    expect(title).toHaveLength(1)
  })

  describe('when I have no bookings', () => {
    it('should render NoItems', () => {
      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when I have just booking of the week', () => {
    it('should render booking of the week', () => {
      // given
      props.isEmpty = false
      props.bookingsOfTheWeek = [
        {
          id: 'b1',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when I have one booking at least', () => {
    it('should render information about "contremarque"', () => {
      // given
      props.isEmpty = false
      props.bookingsOfTheWeek = [
        {
          id: 'b1',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when I have just upcoming booking', () => {
    it('should render upcoming booking', () => {
      // given
      props.isEmpty = false
      props.upComingBookings = [
        {
          id: 'b1',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when I have just finished/cancelled bookings', () => {
    it('should render finished/used/cancelled bookings', () => {
      // given
      props.isEmpty = false
      props.finishedAndUsedAndCancelledBookings = [
        {
          id: 'b1',
        },
        {
          id: 'b2',
        },
      ]

      // when
      const wrapper = shallow(<MyBookingsLists {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
