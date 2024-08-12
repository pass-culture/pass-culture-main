import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { CollectiveBookingStatus, CollectiveOfferStatus } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY } from 'config/swrQueryKeys'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { Mode } from 'core/OfferEducational/types'
import * as useNotification from 'hooks/useNotification'
import {
  getCollectiveOfferCollectiveStockFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  OfferEducationalActions,
  OfferEducationalActionsProps,
} from '../OfferEducationalActions'

vi.mock('apiClient/api', () => ({
  api: {
    patchCollectiveOffersActiveStatus: vi.fn(),
    patchCollectiveOffersTemplateActiveStatus: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const renderOfferEducationalActions = (props: OfferEducationalActionsProps) => {
  return renderWithProviders(<OfferEducationalActions {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedOffererId: 1,
      },
    },
  })
}

describe('OfferEducationalActions', () => {
  const defaultValues = {
    className: 'string',
    isBooked: false,
    offer: getCollectiveOfferFactory(),
    mode: Mode.EDITION,
  }

  it('should update active status value for template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory({
      isActive: false,
      isTemplate: true,
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer: offer,
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier sur ADAGE',
    })

    await userEvent.click(activateOffer)

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      1
    )
    expect(mockMutate).toHaveBeenNthCalledWith(1, [
      GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
      offer.id,
    ])
  })

  it('should failed active status value', async () => {
    const notifyError = vi.fn()
    // @ts-expect-error
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      success: vi.fn(),
      error: notifyError,
    }))
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue({ isOk: false })

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isActive: false,
        isTemplate: true,
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier sur ADAGE',
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
      screen.getByRole('button', { name: 'Masquer la publication sur ADAGE' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display booking link for booked offer', () => {
    const offer = getCollectiveOfferFactory({
      status: CollectiveOfferStatus.SOLD_OUT,
      lastBookingId: 1,
      lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer: offer,
    })
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      `/reservations/collectives?page=1&offerEventDate=${offer.collectiveStock?.startDatetime?.split('T')[0]}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1`
    )
    expect(screen.getByText('réservée')).toBeInTheDocument()
  })

  it('should display booking link for used booking', () => {
    const offer = getCollectiveOfferFactory({
      status: CollectiveOfferStatus.EXPIRED,
      lastBookingId: 1,
      lastBookingStatus: CollectiveBookingStatus.USED,
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer: offer,
    })
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      `/reservations/collectives?page=1&offerEventDate=${offer.collectiveStock?.startDatetime?.split('T')[0]}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1`
    )
    expect(screen.getByText('terminée')).toBeInTheDocument()
  })

  it('should not display booking link for cancelled booking', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        status: CollectiveOfferStatus.ACTIVE,
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
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        status: CollectiveOfferStatus.ACTIVE,
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
        from: '/offre/collectif/recapitulatif',
        offerId: 7,
        offerType: 'collective',
        offererId: '1',
      }
    )
  })

  it('should display error message when trying to activate offer with booking limit date time in the past', async () => {
    const notifyError = vi.fn()
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        isActive: false,
        collectiveStock: getCollectiveOfferCollectiveStockFactory({
          bookingLimitDatetime: '1900-10-15T00:00:00Z',
        }),
      }),
    })
    await userEvent.click(
      screen.getByRole('button', { name: 'Publier sur ADAGE' })
    )
    expect(notifyError).toHaveBeenCalledWith(
      'La date limite de réservation est dépassée. Pour publier l’offre, vous devez modifier la date limite de réservation.'
    )
  })

  it('should activate offer with booking limit date time in the future', async () => {
    const notifyError = vi.fn()
    const offerId = 12

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: vi.fn(),
      error: notifyError,
    }))

    const bookingLimitDateTomorrow = new Date()
    bookingLimitDateTomorrow.setDate(bookingLimitDateTomorrow.getDate() + 1)
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        id: offerId,
        isActive: false,
        collectiveStock: getCollectiveOfferCollectiveStockFactory({
          bookingLimitDatetime: bookingLimitDateTomorrow.toDateString(),
        }),
      }),
    })
    await userEvent.click(
      screen.getByRole('button', { name: 'Publier sur ADAGE' })
    )
    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenCalledWith({
      ids: [offerId],
      isActive: true,
    })
  })

  it('should not display adage publish button when offer is pending', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        status: CollectiveOfferStatus.PENDING,
      }),
    })

    expect(
      screen.queryByRole('button', {
        name: 'Publier sur ADAGE',
      })
    ).not.toBeInTheDocument()
  })
})
