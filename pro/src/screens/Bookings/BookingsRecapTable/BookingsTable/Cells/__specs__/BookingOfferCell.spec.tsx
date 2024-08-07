import { screen } from '@testing-library/react'
import { add } from 'date-fns'

import { collectiveBookingFactory } from 'utils/collectiveApiFactories'
import { bookingRecapFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingOfferCell, BookingOfferCellProps } from '../BookingOfferCell'

const renderOfferCell = (props: BookingOfferCellProps) =>
  renderWithProviders(<BookingOfferCell {...props} />)

describe('bookings offer cell', () => {
  const offerId = 1
  it('offer name and ean with a link to the offer when stock is a book', () => {
    const props: BookingOfferCellProps = {
      booking: collectiveBookingFactory({
        stock: {
          offerId: offerId,
          offerIsbn: '97834567654',
          offerName: 'La Guitare pour les nuls',
          offerIsEducational: false,
          eventBeginningDatetime: new Date().toISOString(),
          eventStartDatetime: new Date().toISOString(),
          numberOfTickets: 1,
        },
      }),
    }

    renderOfferCell(props)

    const ean = screen.getByText('97834567654')
    expect(ean).toBeInTheDocument()
    const title = screen.getByText('La Guitare pour les nuls')
    const title_link = title.closest('a')
    expect(title_link?.href).toContain(`offre/individuelle/${offerId}`)
  })

  it('offer name with a link to the offer when stock is a thing', () => {
    const props: BookingOfferCellProps = {
      booking: collectiveBookingFactory({
        stock: {
          offerId: offerId,
          offerName: 'Guitare acoustique',
          offerIsEducational: false,
          eventBeginningDatetime: new Date().toISOString(),
          eventStartDatetime: new Date().toISOString(),
          numberOfTickets: 1,
        },
      }),
    }

    renderOfferCell(props)

    const offer_name = screen.getByText('Guitare acoustique')
    const offer_name_link = offer_name.closest('a')
    expect(offer_name_link?.href).toContain(`offre/individuelle/${offerId}`)
  })

  it('offer name and event beginning datetime in venue timezone when stock is an event', () => {
    const props: BookingOfferCellProps = {
      booking: collectiveBookingFactory({
        stock: {
          eventBeginningDatetime: '2020-05-12T11:03:28.564687+04:00',
          eventStartDatetime: new Date().toISOString(),
          offerId: offerId,
          offerName: 'La danse des poireaux',
          offerIsEducational: false,
          numberOfTickets: 1,
        },
      }),
    }

    renderOfferCell(props)

    expect(screen.getByText('12/05/2020 11:03')).toBeInTheDocument()
    const offer_name = screen.getByText('La danse des poireaux')
    const offer_name_link = offer_name.closest('a')
    expect(offer_name_link?.href).toContain(`offre/individuelle/${offerId}`)
  })

  it('should display warning when limit booking date is in less than 7 days', () => {
    const tomorrowFns = add(new Date(), {
      days: 1,
    })

    const booking = collectiveBookingFactory({
      stock: {
        bookingLimitDatetime: tomorrowFns.toISOString(),
        eventBeginningDatetime: new Date().toISOString(),
        eventStartDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIsEducational: true,
        offerIsbn: null,
        offerName: 'ma super offre collective',
      },
    })

    renderOfferCell({
      booking,
    })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should not display warning when limit booking date is in more than 7 days', () => {
    const eightDaysFns = add(new Date(), {
      days: 8,
    })

    const booking = collectiveBookingFactory({
      stock: {
        bookingLimitDatetime: eightDaysFns.toISOString(),
        eventBeginningDatetime: new Date().toISOString(),
        eventStartDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIsEducational: false,
        offerIsbn: null,
        offerName: 'ma super offre collective 2',
      },
    })
    renderOfferCell({
      booking,
    })

    expect(
      screen.queryByRole('img', { name: 'Attention' })
    ).not.toBeInTheDocument()
  })

  it('should render tarif informations for individual bookings', () => {
    const booking = bookingRecapFactory({
      bookingAmount: 12,
      bookingPriceCategoryLabel: 'Plein tarif',
    })

    renderOfferCell({
      booking,
    })

    expect(screen.getByText('Plein tarif - 12,00 €')).toBeInTheDocument()
  })
})
