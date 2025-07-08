import { screen } from '@testing-library/react'
import { addDays, format, subDays } from 'date-fns'

import { OfferStatus } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY } from 'commons/utils/date'
import { listOffersOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { OfferBookingCell, OfferBookingCellProps } from './OfferBookingCell'

function renderOfferBookingCell(props: OfferBookingCellProps) {
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferBookingCell {...props} />
        </tr>
      </tbody>
    </table>
  )
}

const defaultProps: OfferBookingCellProps = {
  offer: listOffersOfferFactory({ status: OfferStatus.SCHEDULED }),
  rowId: '',
}

const dayInTheFuture = addDays(new Date(), 2).toISOString()
const dayInThePast = subDays(new Date(), 2).toISOString()

describe('OfferBookingCell', () => {
  it('should show the booking allowed date', () => {
    renderOfferBookingCell({
      ...defaultProps,
      offer: listOffersOfferFactory({
        bookingAllowedDatetime: dayInTheFuture,
        status: OfferStatus.SCHEDULED,
      }),
    })

    expect(
      screen.getByText(new RegExp(format(dayInTheFuture, FORMAT_DD_MM_YYYY)))
    ).toBeInTheDocument()
  })

  it('should show the bookings count if the FF WIP_REFACTO_FUTURE_OFFER is enabled and the offer is already bookable', () => {
    renderOfferBookingCell({
      ...defaultProps,
      offer: listOffersOfferFactory({
        bookingsCount: 111,
        bookingAllowedDatetime: dayInThePast,
      }),
    })

    expect(screen.getByText('111')).toBeInTheDocument()
  })

  it('should show a placeholder if the FF WIP_REFACTO_FUTURE_OFFER is enabled and the offer is already bookable but with no bookings yet', () => {
    renderOfferBookingCell({
      ...defaultProps,
      offer: listOffersOfferFactory({
        bookingsCount: 0,
        bookingAllowedDatetime: dayInThePast,
      }),
    })

    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
