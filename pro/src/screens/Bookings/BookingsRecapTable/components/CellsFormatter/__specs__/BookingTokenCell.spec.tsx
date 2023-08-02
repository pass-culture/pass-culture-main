import { render, screen } from '@testing-library/react'
import React from 'react'

import BookingTokenCell, { BookingTokenCellProps } from '../BookingTokenCell'

const renderBookingTokenCell = (props: BookingTokenCellProps) =>
  render(<BookingTokenCell {...props} />)

describe('BookingTokenCell', () => {
  it('should display a booking token when value is provided', () => {
    const props = {
      bookingToken: 'ABCDEF',
    }

    renderBookingTokenCell(props)

    expect(screen.getByText('ABCDEF')).toBeInTheDocument()
  })

  it('should display a hyphen when value is not provided', () => {
    const props = {
      bookingToken: null,
    }

    renderBookingTokenCell(props)

    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
