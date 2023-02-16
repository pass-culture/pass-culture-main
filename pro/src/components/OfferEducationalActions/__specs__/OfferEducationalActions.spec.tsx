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
  const defaultValues = {
    className: 'string',
    isOfferActive: true,
    isBooked: false,
    offer: collectiveOfferFactory(),
    setIsOfferActive: jest.fn(),
    cancelActiveBookings: jest.fn(),
  }

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions({ ...defaultValues })
    expect(
      screen.getByRole('button', { name: 'Masquer la publication sur Adage' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display booking link for booked offer', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        status: OfferStatus.SOLD_OUT,
        lastBookingId: 1,
        lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
      }),
    })
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      '/reservations/collectives?page=1&offerEventDate=2021-10-15&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1'
    )
    expect(screen.getByText('réservée')).toBeInTheDocument()
  })
  it('should display booking link for used booking', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        status: OfferStatus.EXPIRED,
        lastBookingId: 1,
        lastBookingStatus: CollectiveBookingStatus.USED,
      }),
    })
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      '/reservations/collectives?page=1&offerEventDate=2021-10-15&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1'
    )
    expect(screen.getByText('terminée')).toBeInTheDocument()
  })
  it('should not display booking link for cancelled booking', async () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        status: OfferStatus.ACTIVE,
        lastBookingId: 1,
        lastBookingStatus: CollectiveBookingStatus.CANCELLED,
      }),
    })
    expect(
      screen.queryByRole('link', {
        name: 'Voir la réservation',
      })
    ).not.toBeInTheDocument()
  })
})
