import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import Header from '../Header'

const renderHeader = props => render(<Header {...props} />)

describe("bookings recap table's header", () => {
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
    booking_status: 'validated',
    booking_is_duo: false,
    venue: {
      identifier: 'AE',
      name: 'Librairie Kléber',
    },
  }

  it('should display the appropriate message when there is one booking', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('1 réservation')).toBeInTheDocument()
  })

  it('should display the appropriate message when there is several booking', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap, oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('2 réservations')).toBeInTheDocument()
  })

  it('should display a link to specific csv when not loading', () => {
    // Given
    const bookingsRecapFiltered = [oneBookingRecap]
    const props = {
      bookingsRecapFiltered: bookingsRecapFiltered,
      isLoading: false,
    }

    // When
    renderHeader(props)

    // Then
    const csv_download_link = screen.getByText('Télécharger le CSV')
    expect(csv_download_link.download).toBe('Réservations Pass Culture.csv')
  })

  it('should only display a specific message when data are still loading', () => {
    // Given
    const props = {
      bookingsRecapFiltered: [],
      isLoading: true,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.getByText('Chargement des réservations...')).toBeInTheDocument()
  })
})
