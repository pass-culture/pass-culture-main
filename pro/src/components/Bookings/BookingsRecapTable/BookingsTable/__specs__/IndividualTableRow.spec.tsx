import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { BookingRecapStatus } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualTableRow,
  IndividualTableRowProps,
} from '../IndividualTableRow'

const MOCK_DATA = {
  booking: {
    bookingAmount: 100,
    bookingStatus: BookingRecapStatus.BOOKED,
    bookingStatusHistory: [],
    bookingDate: new Date().toDateString(),
    beneficiary: {
      email: 'john.doe@gmail.com',
      firstname: 'John',
      lastname: 'Doe',
      phonenumber: '123456789',
    },
    bookingIsDuo: false,
    bookingPriceCategoryLabel: null,
    bookingToken: null,
    stock: {
      eventBeginningDatetime: new Date().toDateString(),
      offerId: 1,
      offerIsEducational: false,
      offerName: 'Offer 1',
      stockIdentifier: 1,
    },
  },
  index: 0,
}

const LABELS = {
  detailsPriceTitle: /Prix/,
  detailsHistoryTitle: /Historique/,
  detailsButton: /Détails/,
}

const renderIndividualTableRow = (
  props: Partial<IndividualTableRowProps> = {}
) => {
  const finalProps: IndividualTableRowProps = {
    ...MOCK_DATA,
    ...props,
  }

  return renderWithProviders(
    <table>
      <tbody>
        <IndividualTableRow {...finalProps} />
      </tbody>
    </table>
  )
}

describe('IndividualTableRow', () => {
  it('should hide booking details if row is not expanded', () => {
    renderIndividualTableRow()

    expect(screen.queryByText(LABELS.detailsPriceTitle)).not.toBeInTheDocument()
    expect(
      screen.queryByText(LABELS.detailsHistoryTitle)
    ).not.toBeInTheDocument()
  })

  it('should display booking details if row is expanded', async () => {
    renderIndividualTableRow()

    await userEvent.click(screen.getByText(LABELS.detailsButton))

    expect(screen.getByText(LABELS.detailsPriceTitle)).toBeInTheDocument()
    expect(screen.getByText(LABELS.detailsHistoryTitle)).toBeInTheDocument()
  })

  describe('when booking details are displayed', () => {
    it('should display the booking amount when it is not free', async () => {
      renderIndividualTableRow()

      await userEvent.click(screen.getByText(LABELS.detailsButton))

      expect(screen.getByText(LABELS.detailsPriceTitle)).toBeInTheDocument()
      expect(
        screen.getByText(`${MOCK_DATA.booking.bookingAmount},00 €`)
      ).toBeInTheDocument()
    })

    it('should display the appropriate message when the offer is free', async () => {
      renderIndividualTableRow({
        booking: {
          ...MOCK_DATA.booking,
          bookingAmount: 0,
        },
      })

      await userEvent.click(screen.getByText(LABELS.detailsButton))

      expect(screen.getByText(LABELS.detailsPriceTitle)).toBeInTheDocument()
      expect(screen.getByText(/Gratuit/)).toBeInTheDocument()
    })

    it('should display the booking status history', async () => {
      const bookingStatusHistory = [
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
      ]

      const expectedNumberOfHistoryDates = bookingStatusHistory.length

      renderIndividualTableRow({
        booking: {
          ...MOCK_DATA.booking,
          bookingStatusHistory,
        },
      })

      await userEvent.click(screen.getByText(LABELS.detailsButton))

      expect(screen.getByText(LABELS.detailsHistoryTitle)).toBeInTheDocument()
      const historyCellReserved = screen.getByText(
        'Réservée : 04/01/2020 20:31'
      )
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
})
