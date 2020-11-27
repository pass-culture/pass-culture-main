import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import NoBookingsMessage from '../NoBookingsMessage'

describe('noBookingsMessage', () => {
  it('should render a message indicating that there is no bookings', () => {
    // When
    render(<NoBookingsMessage />)

    // Then
    expect(screen.queryByText('Aucune réservation pour le moment')).toBeInTheDocument()
  })
})
