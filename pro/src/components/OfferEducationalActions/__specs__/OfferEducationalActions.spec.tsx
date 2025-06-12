import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { CollectiveBookingsEvents } from 'commons/core/FirebaseEvents/constants'
import { Mode } from 'commons/core/OfferEducational/types'
import * as useNotification from 'commons/hooks/useNotification'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

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

const renderOfferEducationalActions = (
  props: OfferEducationalActionsProps,
  features: string[] = []
) => {
  return renderWithProviders(<OfferEducationalActions {...props} />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
    features,
  })
}

describe('OfferEducationalActions', () => {
  const defaultValues = {
    className: 'string',
    offer: getCollectiveOfferFactory(),
    mode: Mode.EDITION,
  }
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>

    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: notifySuccess,
      error: notifyError,
    }))
  })

  it('should update active status value for template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory({
      isActive: false,
      isTemplate: true,
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer,
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier',
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

  it('should show error notification when patchCollectiveOffersTemplateActiveStatus api call fails', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue({ isOk: false })

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isActive: false,
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier',
    })

    await userEvent.click(activateOffer)

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      1
    )
    await waitFor(() => expect(notifyError).toHaveBeenCalledTimes(1))
  })

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isActive: false,
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })
    expect(
      screen.getByRole('button', { name: 'Mettre en pause' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display booking link for booked offer', () => {
    const offer = getCollectiveOfferFactory({
      displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
      booking: {
        id: 1,
        status: CollectiveBookingStatus.CONFIRMED,
      },
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer,
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
      displayedStatus: CollectiveOfferDisplayedStatus.REIMBURSED,
      booking: {
        id: 1,
        status: CollectiveBookingStatus.USED,
      },
    })
    renderOfferEducationalActions({
      ...defaultValues,
      offer,
    })
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      `/reservations/collectives?page=1&offerEventDate=${offer.collectiveStock?.startDatetime?.split('T')[0]}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1`
    )
    expect(screen.getByText('remboursée')).toBeInTheDocument()
  })

  it('should not display booking link for cancelled booking', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        booking: {
          id: 1,
          status: CollectiveBookingStatus.CANCELLED,
        },
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
        booking: {
          id: 1,
          status: CollectiveBookingStatus.CONFIRMED,
        },
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
        offerId: 8,
        offerType: 'collective',
        offererId: '1',
      }
    )
  })

  it('should not display adage publish button when action is not allowed', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        isTemplate: true,
      }),
    })

    expect(
      screen.queryByRole('button', {
        name: 'Publier',
      })
    ).not.toBeInTheDocument()
  })

  it('should not display adage deactivation button when action is not allowed', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferFactory({
        isTemplate: true,
      }),
    })

    expect(
      screen.queryByRole('button', {
        name: 'Mettre en pause',
      })
    ).not.toBeInTheDocument()
  })

  it('should show success notification when template publication succeeds', async () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Publier',
      })
    )

    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre offre est maintenant active et visible dans ADAGE'
    )
  })

  it('should show success notification when template deactivation succeeds', async () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Mettre en pause',
      })
    )

    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre offre est mise en pause et n’est plus visible sur ADAGE'
    )
  })
})
