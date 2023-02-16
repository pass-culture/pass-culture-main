import { screen } from '@testing-library/react'
import React from 'react'

import { CollectiveBookingStatus, OfferStatus } from 'apiClient/v1'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalActions, {
  IOfferEducationalActions,
} from '../OfferEducationalActions'

const renderOfferEducationalActions = (props: IOfferEducationalActions) => {
  return renderWithProviders(<OfferEducationalActions {...props} />)
}

describe('OfferEducationalActions', () => {
  let props: IOfferEducationalActions
  beforeEach(() => {
    props = {
      className: 'string',
      isOfferActive: true,
      isBooked: false,
      offer: collectiveOfferFactory(),
      setIsOfferActive: jest.fn(),
      cancelActiveBookings: jest.fn(),
    }
  })

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions(props)
    expect(
      screen.getByRole('button', { name: 'Masquer la publication sur Adage' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display booking link for booked offer', () => {
    props.offer = collectiveOfferFactory({
      status: OfferStatus.SOLD_OUT,
      lastBookingId: 1,
      lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
    })
    renderOfferEducationalActions(props)
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      '/reservations/collectives?page=1&offerEventDate=2021-10-15&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1'
    )
    expect(screen.getByText('réservée')).toBeInTheDocument()
  })
  it('should display booking link for used booking', () => {
    props.offer = collectiveOfferFactory({
      status: OfferStatus.EXPIRED,
      lastBookingId: 1,
      lastBookingStatus: CollectiveBookingStatus.USED,
    })
    renderOfferEducationalActions(props)
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      '/reservations/collectives?page=1&offerEventDate=2021-10-15&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1'
    )
    expect(screen.getByText('terminée')).toBeInTheDocument()
  })
})
