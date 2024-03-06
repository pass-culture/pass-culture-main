import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { BookingRecapStatus } from 'apiClient/v1'
import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualBookingStatusCell,
  IndividualBookingStatusCellProps,
} from '../IndividualBookingStatusCell'

const renderIndividualBookingStatusCell = (
  props: IndividualBookingStatusCellProps
) => renderWithProviders(<IndividualBookingStatusCell {...props} />)

describe('IndividualBookingsStatusCell', () => {
  it('should display the status label', () => {
    const props = {
      booking: bookingRecapFactory({
        stock: bookingRecapStockFactory({
          eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
          offerName: 'Matrix',
        }),
        bookingIsDuo: true,
        beneficiary: {
          email: 'loulou.duck@example.com',
          firstname: 'Loulou',
          lastname: 'Duck',
        },
        bookingDate: '2020-01-04T20:31:12+01:00',
        bookingToken: '5U7M6U',
        bookingStatus: BookingRecapStatus.VALIDATED,
        bookingStatusHistory: [
          {
            status: BookingRecapStatus.BOOKED,
            date: '2020-01-04T20:31:12+01:00',
          },
        ],
      }),
    }

    renderIndividualBookingStatusCell(props)

    const title = screen.getByText('validée', { selector: 'span' })
    expect(title).toBeInTheDocument()
  })

  it('should display the offer title and history title and amount when it is not free', async () => {
    const expectedHistoryTitle = 'Historique'
    const props = {
      booking: bookingRecapFactory({
        stock: bookingRecapStockFactory({
          eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
          offerName: 'Matrix',
        }),
        bookingIsDuo: true,
        beneficiary: {
          email: 'loulou.duck@example.com',
          firstname: 'Loulou',
          lastname: 'Duck',
        },
        bookingDate: '2020-01-04T20:31:12+01:00',
        bookingToken: '5U7M6U',
        bookingStatus: BookingRecapStatus.BOOKED,
        bookingAmount: 10,
        bookingStatusHistory: [
          {
            status: BookingRecapStatus.BOOKED,
            date: '2020-01-04T20:31:12+01:00',
          },
        ],
      }),
    }

    renderIndividualBookingStatusCell(props)

    const tooltipButton = screen.getByRole('button')
    await userEvent.click(tooltipButton)

    const title = screen.getByText(expectedHistoryTitle, { selector: 'div' })
    expect(title).toBeInTheDocument()
    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText(`Prix : 10,00 €`, { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display the booking amount when it is not free', async () => {
    const props = {
      booking: bookingRecapFactory({
        stock: bookingRecapStockFactory({
          eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
          offerName: 'Matrix',
        }),
        bookingIsDuo: true,
        beneficiary: {
          email: 'loulou.duck@example.com',
          firstname: 'Loulou',
          lastname: 'Duck',
        },
        bookingDate: '2020-01-04T20:31:12+01:00',
        bookingToken: '5U7M6U',
        bookingStatus: BookingRecapStatus.BOOKED,
        bookingAmount: 10,
        bookingStatusHistory: [
          {
            status: BookingRecapStatus.BOOKED,
            date: '2020-01-04T20:31:12+01:00',
          },
        ],
      }),
    }

    renderIndividualBookingStatusCell(props)

    const tooltipButton = screen.getByRole('button')
    await userEvent.click(tooltipButton)

    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText('Prix : 10,00 €', { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display the appropriate message when the offer is free', async () => {
    const props = {
      isCollectiveStatus: false,
      booking: bookingRecapFactory({
        stock: bookingRecapStockFactory({
          eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
          offerName: 'Matrix',
        }),
        bookingIsDuo: true,
        beneficiary: {
          email: 'loulou.duck@example.com',
          firstname: 'Loulou',
          lastname: 'Duck',
        },
        bookingDate: '2020-01-04T20:31:12+01:00',
        bookingToken: '5U7M6U',
        bookingStatus: BookingRecapStatus.BOOKED,
        bookingStatusHistory: [
          {
            status: BookingRecapStatus.BOOKED,
            date: '2020-01-04T20:31:12+01:00',
          },
        ],
      }),
    }

    renderIndividualBookingStatusCell(props)

    const tooltipButton = screen.getByRole('button')
    await userEvent.click(tooltipButton)

    const offer = screen.getByText('Matrix', { selector: 'div' })
    expect(offer).toBeInTheDocument()
    const amount = screen.getByText('Prix : Gratuit', { selector: 'div' })
    expect(amount).toBeInTheDocument()
  })

  it('should display all the history dates present in booking recap history', async () => {
    const expectedNumberOfHistoryDates = 3
    const props = {
      isCollectiveStatus: false,
      booking: bookingRecapFactory({
        stock: bookingRecapStockFactory({
          eventBeginningDatetime: '2020-06-05T16:31:59.102163+02:00',
          offerName: 'Matrix',
        }),
        bookingIsDuo: true,
        beneficiary: {
          email: 'loulou.duck@example.com',
          firstname: 'Loulou',
          lastname: 'Duck',
        },
        bookingDate: '2020-01-04T20:31:12+01:00',
        bookingToken: '5U7M6U',
        bookingStatus: BookingRecapStatus.BOOKED,
        bookingStatusHistory: [
          {
            status: BookingRecapStatus.BOOKED,
            date: '2020-01-04T20:31:12+01:00',
          },
          {
            status: BookingRecapStatus.VALIDATED,
            date: '2020-01-05T20:31:12+01:00',
          },
          {
            status: BookingRecapStatus.REIMBURSED,
            date: '2020-01-06T20:31:12+01:00',
          },
        ],
      }),
    }

    renderIndividualBookingStatusCell(props)

    const tooltipButton = screen.getByRole('button')
    await userEvent.click(tooltipButton)

    const historyCellReserved = screen.getByText('Réservée : 04/01/2020 20:31')
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
