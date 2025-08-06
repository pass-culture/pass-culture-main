import { screen } from '@testing-library/react'

import { BookingRecapStatus } from '@/apiClient/v1'
import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

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
})
