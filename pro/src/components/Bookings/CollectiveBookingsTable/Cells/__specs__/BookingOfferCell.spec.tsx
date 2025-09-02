import { screen } from '@testing-library/react'
import { add } from 'date-fns'

import { collectiveBookingFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  BookingOfferCell,
  type BookingOfferCellProps,
} from '../BookingOfferCell'

const renderOfferCell = (props: BookingOfferCellProps) =>
  renderWithProviders(<BookingOfferCell {...props} />)

describe('bookings offer cell', () => {
  const offerId = 1

  it('should display warning when limit booking date is in less than 7 days', () => {
    const tomorrowFns = add(new Date(), {
      days: 1,
    })

    const booking = collectiveBookingFactory({
      stock: {
        bookingLimitDatetime: tomorrowFns.toISOString(),
        eventStartDatetime: new Date().toISOString(),
        eventEndDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIsEducational: true,
        offerEan: null,
        offerName: 'ma super offre collective',
      },
    })

    renderOfferCell({ booking })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should not display warning when limit booking date is in more than 7 days', () => {
    const eightDaysFns = add(new Date(), {
      days: 8,
    })

    const booking = collectiveBookingFactory({
      stock: {
        bookingLimitDatetime: eightDaysFns.toISOString(),
        eventStartDatetime: new Date().toISOString(),
        eventEndDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIsEducational: true,
        offerEan: null,
        offerName: 'ma super offre collective 2',
      },
    })
    renderOfferCell({ booking })

    expect(
      screen.queryByRole('img', { name: 'Attention' })
    ).not.toBeInTheDocument()
  })
})
