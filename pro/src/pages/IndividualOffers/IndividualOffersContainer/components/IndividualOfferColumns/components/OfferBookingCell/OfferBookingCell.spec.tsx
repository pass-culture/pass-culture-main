import { screen } from '@testing-library/react'
import { addDays, format, subDays } from 'date-fns'

import { OfferStatus } from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { listOffersOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferBookingCell,
  type OfferBookingCellProps,
} from './OfferBookingCell'

function renderOfferBookingCell(props: OfferBookingCellProps) {
  renderWithProviders(<OfferBookingCell {...props} />)
}

const defaultProps: OfferBookingCellProps = {
  offer: listOffersOfferFactory({ status: OfferStatus.SCHEDULED }),
}

describe('OfferBookingCell', () => {
  let dayInTheFuture: string
  let dayInThePast: string

  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-09-01T12:00:00.000Z'))

    dayInTheFuture = addDays(new Date(), 2).toISOString()
    dayInThePast = subDays(new Date(), 2).toISOString()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

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

  it('should show the bookings count if the offer is already bookable', () => {
    renderOfferBookingCell({
      ...defaultProps,
      offer: listOffersOfferFactory({
        bookingsCount: 111,
        bookingAllowedDatetime: dayInThePast,
      }),
    })

    expect(screen.getByText('111')).toBeInTheDocument()
  })

  it('should show a placeholder if the offer is already bookable but with no bookings yet', () => {
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
