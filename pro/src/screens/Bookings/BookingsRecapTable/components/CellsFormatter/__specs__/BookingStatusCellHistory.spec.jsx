import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import BookingStatusCellHistory from '../BookingStatusCellHistory'

const renderBookingStatusCellHistory = props =>
  render(<BookingStatusCellHistory {...props} />)

describe('bookings status history cell', () => {
  it('should display the corresponding status and date when the offer is booked', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'booked',
          date: '2020-01-04T20:31:12+02:00',
        },
      ],
    }

    // When
    renderBookingStatusCellHistory(props)

    // Then
    expect(screen.getByText('Réservé : 04/01/2020 20:31')).toBeInTheDocument()
  })

  it('should display the corresponding status and date when the offer is pending', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'pending',
          date: '2020-01-04T20:31:12+02:00',
        },
      ],
    }

    // When
    renderBookingStatusCellHistory(props)

    // Then
    expect(
      screen.getByText('Préréservé (scolaire) : 04/01/2020 20:31')
    ).toBeInTheDocument()
  })

  describe('should display proper infos', () => {
    it('for booked status', () => {
      // Given
      const props = {
        bookingStatusHistory: [
          {
            status: 'booked',
            date: '2020-01-04T20:31:12+01:00',
          },
        ],
      }

      // When
      renderBookingStatusCellHistory(props)

      // Then
      expect(screen.getByText('Réservé : 04/01/2020 20:31')).toBeInTheDocument()
    })
    it('for validated status', () => {
      // Given
      const props = {
        bookingStatusHistory: [
          {
            status: 'validated',
            date: '2020-01-05T20:31:12+01:00',
          },
        ],
      }

      // When
      renderBookingStatusCellHistory(props)

      // Then
      expect(
        screen.getByText('Réservation validée : 05/01/2020 20:31')
      ).toBeInTheDocument()
    })
    it('for reimbursed status', () => {
      // Given
      const props = {
        bookingStatusHistory: [
          {
            status: 'reimbursed',
            date: '2020-01-06T20:31:12+01:00',
          },
        ],
      }

      // When
      renderBookingStatusCellHistory(props)

      // Then
      expect(screen.getByText('Remboursée : 06/01/2020')).toBeInTheDocument()
    })
    it('for confirmed status', () => {
      // Given
      const props = {
        bookingStatusHistory: [
          {
            status: 'confirmed',
            date: '2020-01-06T20:31:12+01:00',
          },
        ],
      }

      // When
      renderBookingStatusCellHistory(props)

      // Then
      expect(
        screen.getByText('Réservation confirmée : 06/01/2020 20:31')
      ).toBeInTheDocument()
    })
  })

  it('should display only the date without the time for reimbursed status history', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    // When
    renderBookingStatusCellHistory(props)

    // Then
    expect(screen.getByText('Remboursée : 06/01/2020')).toBeInTheDocument()
  })

  it('should display a "-" when the date is not available', () => {
    // Given
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: null,
        },
      ],
    }

    // When
    renderBookingStatusCellHistory(props)

    // Then
    expect(screen.getByText('Remboursée : -')).toBeInTheDocument()
  })
})
