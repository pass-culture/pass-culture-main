import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import BookingDateCell from '../BookingDateCell'

const renderDateCell = props => render(<BookingDateCell {...props} />)

describe('bookings date cell', () => {
  it('should display the date and the time', () => {
    // Given
    const props = {
      bookingDateTimeIsoString: '2020-04-03T12:00:00+04:00',
    }

    // When
    renderDateCell(props)

    // Then
    expect(screen.getByText('03/04/2020')).toBeInTheDocument()
    expect(screen.getByText('12:00')).toBeInTheDocument()
  })
})
