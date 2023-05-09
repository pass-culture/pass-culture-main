import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { CollectiveBookingStatus, OfferStatus } from 'apiClient/v1'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { Mode } from 'core/OfferEducational/types'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
  collectiveStockFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalActions, {
  IOfferEducationalActions,
} from '../OfferEducationalActions'

jest.mock('apiClient/api', () => ({
  api: {
    patchCollectiveOffersActiveStatus: jest.fn(),
    patchCollectiveOffersTemplateActiveStatus: jest.fn(),
  },
}))

const renderOfferEducationalActions = (props: IOfferEducationalActions) => {
  return renderWithProviders(<OfferEducationalActions {...props} />)
}

describe('OfferEducationalActions', () => {
  const defaultValues = {
    className: 'string',
    isBooked: false,
    offer: collectiveOfferFactory(),
    reloadCollectiveOffer: jest.fn(),
    mode: Mode.EDITION,
  }

  it('should update active status value for template offer', async () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferTemplateFactory({
        isActive: false,
        isTemplate: true,
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier sur Adage',
    })

    await userEvent.click(activateOffer)

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      1
    )
    expect(defaultValues.reloadCollectiveOffer).toHaveBeenCalledTimes(1)
  })

  it('should failed active status value', async () => {
    const notifyError = jest.fn()
    // @ts-expect-error
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: jest.fn(),
      error: notifyError,
    }))
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockRejectedValue({ isOk: false })

    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferTemplateFactory({
        isActive: false,
        isTemplate: true,
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier sur Adage',
    })

    await userEvent.click(activateOffer)

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      1
    )
    await waitFor(() => expect(notifyError).toHaveBeenCalledTimes(1))
  })

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions({ ...defaultValues, isBooked: false })
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

  it('should display error message when trying to activate offer with booking limit date time in the past', async () => {
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        isActive: false,
        collectiveStock: collectiveStockFactory({
          bookingLimitDatetime: '1900-10-15T00:00:00Z',
        }),
      }),
    })
    await userEvent.click(
      screen.getByRole('button', { name: 'Publier sur Adage' })
    )
    expect(notifyError).toHaveBeenCalledWith(
      'La date limite de réservation est dépassée. Pour publier l’offre, vous devez modifier la date limite de réservation.'
    )
  })

  it('should activate offer with booking limit date time in the future', async () => {
    const notifyError = jest.fn()
    const offerId = 12
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      success: jest.fn(),
      error: notifyError,
    }))
    const bookingLimitDateTomorrow = new Date()
    bookingLimitDateTomorrow.setDate(bookingLimitDateTomorrow.getDate() + 1)
    renderOfferEducationalActions({
      ...defaultValues,
      offer: collectiveOfferFactory({
        id: 'AE',
        nonHumanizedId: offerId,
        isActive: false,
        collectiveStock: collectiveStockFactory({
          bookingLimitDatetime: bookingLimitDateTomorrow.toDateString(),
        }),
      }),
    })
    await userEvent.click(
      screen.getByRole('button', { name: 'Publier sur Adage' })
    )
    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenCalledWith({
      ids: [offerId],
      isActive: true,
    })
  })
})
