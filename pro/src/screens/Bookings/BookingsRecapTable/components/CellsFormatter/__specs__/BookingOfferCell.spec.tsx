import { screen } from '@testing-library/react'
import { add } from 'date-fns'
import React from 'react'
import { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { collectiveBookingRecapFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingOfferCell, { BookingOfferCellProps } from '../BookingOfferCell'

const renderOfferCell = (props: BookingOfferCellProps) =>
  renderWithProviders(<BookingOfferCell {...props} />)

describe('bookings offer cell', () => {
  const offerId = 1
  it('offer name and ean with a link to the offer when stock is a book', () => {
    const props = {
      offer: {
        offerIdentifier: 'A0',
        offerId: offerId,
        offerIsbn: '97834567654',
        offerName: 'La Guitare pour les nuls',
        type: 'book',
        venueDepartmentCode: '93',
        offerIsEducational: false,
        eventBeginningDatetime: new Date().toISOString(),
        numberOfTickets: 1,
      },
      bookingRecapInfo: {
        original: collectiveBookingRecapFactory(),
      } as Row<CollectiveBookingResponseModel>,
      isCollective: false,
    }

    renderOfferCell(props)

    const ean = screen.getByText('97834567654')
    expect(ean).toBeInTheDocument()
    const title = screen.getByText('La Guitare pour les nuls')
    const title_link = title.closest('a')
    expect(title_link?.href).toContain(`offre/individuelle/${offerId}`)
    expect(title_link?.target).toContain('_blank')
  })

  it('offer name with a link to the offer when stock is a thing', () => {
    const props = {
      offer: {
        offerIdentifier: 'A1',
        offerId: offerId,
        offerName: 'Guitare acoustique',
        type: 'thing',
        venueDepartmentCode: '93',
        offerIsEducational: false,
        eventBeginningDatetime: new Date().toISOString(),
        numberOfTickets: 1,
      },
      bookingRecapInfo: {
        original: collectiveBookingRecapFactory(),
      } as Row<CollectiveBookingResponseModel>,
      isCollective: false,
    }

    renderOfferCell(props)

    const offer_name = screen.getByText('Guitare acoustique')
    const offer_name_link = offer_name.closest('a')
    expect(offer_name_link?.href).toContain(`offre/individuelle/${offerId}`)
    expect(offer_name_link?.target).toContain('_blank')
  })

  it('offer name and event beginning datetime in venue timezone when stock is an event', () => {
    const props = {
      offer: {
        eventBeginningDatetime: '2020-05-12T11:03:28.564687+04:00',
        offerIdentifier: 'A2',
        offerId: offerId,
        offerName: 'La danse des poireaux',
        type: 'event',
        venueDepartmentCode: '93',
        offerIsEducational: false,
        numberOfTickets: 1,
      },
      bookingRecapInfo: {
        original: collectiveBookingRecapFactory(),
      } as Row<CollectiveBookingResponseModel>,
      isCollective: false,
    }

    renderOfferCell(props)

    expect(screen.getByText('12/05/2020 11:03')).toBeInTheDocument()
    const offer_name = screen.getByText('La danse des poireaux')
    const offer_name_link = offer_name.closest('a')
    expect(offer_name_link?.href).toContain(`offre/individuelle/${offerId}`)
    expect(offer_name_link?.target).toContain('_blank')
  })

  it('should display warning when limit booking date is in less than 7 days', () => {
    const tomorrowFns = add(new Date(), {
      days: 1,
    })

    const eventOffer = collectiveBookingRecapFactory({
      stock: {
        bookingLimitDatetime: tomorrowFns.toISOString(),
        eventBeginningDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIdentifier: '1',
        offerIsEducational: true,
        offerIsbn: null,
        offerName: 'ma super offre collective',
      },
    })

    renderOfferCell({
      offer: eventOffer.stock,
      bookingRecapInfo: {
        original: eventOffer,
        values: eventOffer,
      } as unknown as Row<CollectiveBookingResponseModel>,
      isCollective: true,
    })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should not display warning when limit booking date is in more than 7 days', () => {
    const eightDaysFns = add(new Date(), {
      days: 8,
    })

    const eventOffer = collectiveBookingRecapFactory({
      stock: {
        bookingLimitDatetime: eightDaysFns.toISOString(),
        eventBeginningDatetime: new Date().toISOString(),
        numberOfTickets: 1,
        offerId: offerId,
        offerIdentifier: '1',
        offerIsEducational: true,
        offerIsbn: null,
        offerName: 'ma super offre collective 2',
      },
    })
    renderOfferCell({
      offer: eventOffer.stock,
      bookingRecapInfo: {
        original: eventOffer,
      } as Row<CollectiveBookingResponseModel>,
      isCollective: false,
    })

    expect(
      screen.queryByRole('img', { name: 'Attention' })
    ).not.toBeInTheDocument()
  })
})
