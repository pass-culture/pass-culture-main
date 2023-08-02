import { screen } from '@testing-library/react'
import React from 'react'
import { Row } from 'react-table'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingStatusCell, { BookingStatusCellProps } from '../BookingStatusCell'

const renderBookingStatusCell = (props: BookingStatusCellProps) =>
  renderWithProviders(<BookingStatusCell {...props} />)

describe('BookingsStatusCell', () => {
  it('should display the status label', () => {
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'validated',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-01-04T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const title = screen.getByText('validée', { selector: 'span' })
    expect(title).toBeInTheDocument()
  })

  it('should display the pending status label', () => {
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'pending',
          bookingStatusHistory: [
            {
              status: 'pending',
              date: '2020-01-04T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const title = screen.getByText('préréservé', { selector: 'span' })
    expect(title).toBeInTheDocument()
  })

  it('should display the offer title and history title and amount when it is not free', () => {
    const expectedHistoryTitle = 'Historique'
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'booked',
          bookingAmount: '10',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-01-04T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const title = screen.getByText(expectedHistoryTitle, { selector: 'div' })
    expect(title).toBeInTheDocument()
    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText(`Prix : 10 €`, { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display the booking amount when it is not free', () => {
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'booked',
          bookingAmount: '10',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-01-04T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText('Prix : 10 €', { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display the appropriate message when the offer is free', () => {
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'booked',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-01-04T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText('Prix : Gratuit', { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display all the history dates present in booking recap history', () => {
    const expectedNumberOfHistoryDates = 3
    const props = {
      isCollectiveStatus: false,
      bookingRecapInfo: {
        original: {
          stock: {
            eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
            offerName: 'Matrix',
            type: 'event',
          },
          bookingIsDuo: true,
          beneficiary: {
            email: 'loulou.duck@example.com',
            firstname: 'Loulou',
            lastname: 'Duck',
          },
          bookingDate: '2020-01-04T20:31:12+01:00',
          bookingToken: '5U7M6U',
          bookingStatus: 'booked',
          bookingStatusHistory: [
            {
              status: 'booked',
              date: '2020-01-04T20:31:12+01:00',
            },
            {
              status: 'validated',
              date: '2020-01-05T20:31:12+01:00',
            },
            {
              status: 'reimbursed',
              date: '2020-01-06T20:31:12+01:00',
            },
          ],
        },
      } as unknown as Row<BookingRecapResponseModel>,
    }

    renderBookingStatusCell(props)

    const historyCellReserved = screen.getByText('Réservé : 04/01/2020 20:31')
    expect(historyCellReserved).toBeInTheDocument()
    const historyCellValidated = screen.getByText(
      'Réservation validée : 05/01/2020 20:31'
    )
    expect(historyCellValidated).toBeInTheDocument()
    const historyCellReimbursed = screen.getByText('Remboursée : 06/01/2020')
    expect(historyCellReimbursed).toBeInTheDocument()
    const numberOfHistoryItemsDisplayed = screen.getAllByRole('listitem')
    expect(numberOfHistoryItemsDisplayed).toHaveLength(
      expectedNumberOfHistoryDates
    )
  })
})
