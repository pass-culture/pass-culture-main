import { shallow } from 'enzyme'
import React from 'react'
import Header from '../Header'

describe('components | Header', () => {
  it('should render "1 réservation" when one booking', () => {
    // Given
    const props = {
      nbBookings: 1,
      isLoading: false,
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: '1 réservation' })
    expect(header).toHaveLength(1)
  })

  it('should render "2 réservations" when two bookings', () => {
    // Given
    const props = {
      nbBookings: 2,
      isLoading: false,
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: '2 réservations' })
    expect(header).toHaveLength(1)
  })

  it('should render "Chargement des réservations en cours" when data are still loading', () => {
    // Given
    const props = {
      nbBookings: 2,
      isLoading: true,
    }

    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: 'Chargement des réservations...' })
    expect(header).toHaveLength(1)
  })
})
