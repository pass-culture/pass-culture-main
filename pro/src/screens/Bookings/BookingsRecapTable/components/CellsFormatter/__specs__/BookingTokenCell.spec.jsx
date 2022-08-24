import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import BookingTokenCell from '../BookingTokenCell'

const renderBookingTokenCell = props => render(<BookingTokenCell {...props} />)

describe('bookings token cell', () => {
  it('should display a booking token when value is provided', () => {
    // Given
    const props = {
      bookingToken: 'ABCDEF',
    }

    // When
    renderBookingTokenCell(props)

    // Then
    expect(screen.getByText('ABCDEF')).toBeInTheDocument()
  })

  it('should display a hyphen when value is not provided', () => {
    // Given
    const props = {
      bookingToken: null,
    }

    // When
    renderBookingTokenCell(props)

    // Then
    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
