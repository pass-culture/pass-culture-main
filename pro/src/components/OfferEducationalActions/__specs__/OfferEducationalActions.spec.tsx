import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { CollectiveBookingStatus, OfferStatus } from 'apiClient/v1'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
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
  it('should log event when clicked on booking link', async () => {
    const mockLogEvent = jest.fn()
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        status: OfferStatus.ACTIVE,
        lastBookingId: 1,
        lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
      }),
    })
    const bookingLink = screen.getByRole('link', {
      name: 'Voir la réservation',
    })
    await userEvent.click(bookingLink)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
      {
        from: '/',
      }
    )
  })
})
