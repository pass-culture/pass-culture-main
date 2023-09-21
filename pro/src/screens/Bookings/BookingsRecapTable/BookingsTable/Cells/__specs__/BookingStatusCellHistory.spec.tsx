import { render, screen } from '@testing-library/react'
import React from 'react'

import { BookingRecapStatus } from 'apiClient/v1'

import {
  BookingStatusCellHistory,
  BookingStatusCellHistoryProps,
} from '../BookingStatusCellHistory'

const renderBookingStatusCellHistory = (props: BookingStatusCellHistoryProps) =>
  render(<BookingStatusCellHistory {...props} />)

describe('bookings status history cell', () => {
  it('should display the corresponding status and date when the offer is booked', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'booked',
          date: '2020-01-04T20:31:12+02:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(screen.getByText('Réservé : 04/01/2020 20:31')).toBeInTheDocument()
  })

  it('should display the corresponding status and date when the offer is pending', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'pending',
          date: '2020-01-04T20:31:12+02:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(
      screen.getByText('Préréservé (scolaire) : 04/01/2020 20:31')
    ).toBeInTheDocument()
  })

  it('should display proper infos for booked status', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'booked',
          date: '2020-01-04T20:31:12+01:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(screen.getByText('Réservé : 04/01/2020 20:31')).toBeInTheDocument()
  })

  it('should display proper infos for validated status', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'validated',
          date: '2020-01-05T20:31:12+01:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(
      screen.getByText('Réservation validée : 05/01/2020 20:31')
    ).toBeInTheDocument()
  })

  it('should display proper infos for reimbursed status', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(screen.getByText('Remboursée : 06/01/2020')).toBeInTheDocument()
  })

  it('should display proper infos for confirmed status', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'confirmed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(
      screen.getByText('Réservation confirmée : 06/01/2020 20:31')
    ).toBeInTheDocument()
  })

  it('should display only the date without the time for reimbursed status history', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: 'reimbursed',
          date: '2020-01-06T20:31:12+01:00',
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(screen.getByText('Remboursée : 06/01/2020')).toBeInTheDocument()
  })

  it('should display a "-" when the date is not available', () => {
    const props = {
      bookingStatusHistory: [
        {
          status: BookingRecapStatus.REIMBURSED,
          date: null,
        },
      ],
    }

    renderBookingStatusCellHistory(props)

    expect(screen.getByText('Remboursée : -')).toBeInTheDocument()
  })
})
