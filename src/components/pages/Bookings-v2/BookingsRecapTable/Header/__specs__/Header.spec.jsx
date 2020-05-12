import { shallow } from 'enzyme'
import React from 'react'
import Header from '../Header'

describe('components | Header', () => {
  it('should render "Aucune réservation" when no bookings', () => {
    // Given
    const props = {
      nbBookings: 0
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: 'Aucune réservation'})
    expect(header).toHaveLength(1)
  })

  it('should render "1 réservation" when one booking', () => {
    // Given
    const props = {
      nbBookings: 1
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: '1 réservation'})
    expect(header).toHaveLength(1)
  })

  it('should render "2 réservations" when two bookings', () => {
    // Given
    const props = {
      nbBookings: 2
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: '2 réservations'})
    expect(header).toHaveLength(1)
  })
})
