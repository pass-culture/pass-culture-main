import { mount } from 'enzyme'
import React from 'react'
import Header from '../Header'

describe('components | Header', () => {
  const oneBookingRecap = {
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
    booking_status: 'Validé',
    booking_is_duo: false,
    venue_identifier: 'AE',
  }

  it('should render "1 réservation" when one booking', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    const wrapper = mount(<Header {...props} />)

    // Then
    const numberOfBookings = wrapper.find({ children: '1 réservation' })
    expect(numberOfBookings).toHaveLength(1)
  })

  it('should render "2 réservations" when two bookings', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap, oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    const wrapper = mount(<Header {...props} />)

    // Then
    const numberOfBookings = wrapper.find({ children: '2 réservations' })
    expect(numberOfBookings).toHaveLength(1)
  })

  it('should render "Télécharger le CSV" link when not loading', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    const wrapper = mount(<Header {...props} />)

    // Then
    const downloadCsvLink = wrapper.find('a')
    expect(downloadCsvLink).toHaveLength(1)
    expect(downloadCsvLink.text()).toBe('Télécharger le CSV')
    expect(downloadCsvLink.prop('download')).toBe('Réservations Pass Culture.csv')
  })

  it('should render "Chargement des réservations en cours" when data are still loading and nothing else', () => {
    // Given
    const props = {
      bookingsRecapFiltered: [],
      isLoading: true,
    }

    // When
    const wrapper = mount(<Header {...props} />)

    // Then
    const header = wrapper.find({ children: 'Chargement des réservations...' })
    expect(header).toHaveLength(1)
    const numberOfBookings = wrapper.find("[children^='réservation']")
    expect(numberOfBookings).toHaveLength(0)
    const downloadCsvLink = wrapper.find('a')
    expect(downloadCsvLink).toHaveLength(0)
  })
})
