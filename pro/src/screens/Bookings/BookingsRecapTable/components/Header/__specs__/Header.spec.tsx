import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import Header, { HeaderProps } from '../Header'

const renderHeader = (props: HeaderProps) => render(<Header {...props} />)

describe("bookings recap table's header", () => {
  it('should display the appropriate message when there is one booking', () => {
    // Given
    const props = {
      bookingsRecapFilteredLength: 1,
      isLoading: false,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('1 réservation')).toBeInTheDocument()
  })

  it('should display the appropriate message when there is several booking', () => {
    // Given
    const props = {
      bookingsRecapFilteredLength: 2,
      isLoading: false,
    }

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('2 réservations')).toBeInTheDocument()
  })

  it('should only display a specific message when data are still loading', () => {
    // Given
    const props = {
      bookingsRecapFilteredLength: 0,
      isLoading: true,
    }

    // When
    renderHeader(props)

    // Then
    expect(
      screen.getByText('Chargement des réservations...')
    ).toBeInTheDocument()
  })
})
