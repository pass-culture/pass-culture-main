import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays } from 'date-fns'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError, CollectiveOfferAllowedAction } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { BOOKING_STATUS } from 'commons/core/Bookings/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import * as useNotification from 'commons/hooks/useNotification'
import {
  collectiveBookingCollectiveStockFactory,
  collectiveBookingFactory,
  getCollectiveOfferFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  CollectiveActionButtons,
  CollectiveActionButtonsProps,
} from '../CollectiveActionButtons'

const renderCollectiveActionButtons = (props: CollectiveActionButtonsProps, features: string[] = []
) => {
  renderWithProviders(<CollectiveActionButtons {...props} />, { features })
}

describe('CollectiveActionButtons', () => {
  it('should display modify offer button for pending booking', () => {
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
    })
    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: false,
    })
    const modifyLink = screen.getByRole('link', { name: 'Modifier l’offre' })
    expect(modifyLink).toBeInTheDocument()
    expect(modifyLink).toHaveAttribute(
      'href',
      '/offre/1/collectif/recapitulatif'
    )
  })
  it('should not display modify offer button for validated booking for more than 2 days', () => {
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: collectiveBookingCollectiveStockFactory({
        eventBeginningDatetime: addDays(new Date(), 3).toISOString(),
      }),
    })
    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: false,
    })
    expect(
      screen.queryByRole('link', { name: 'Modifier l’offre' })
    ).not.toBeInTheDocument()
  })
})

describe('collectiveActionButton api call', () => {
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()
  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
      success: notifySuccess,
    }))
  })

  it('should return an error when the offer id is not valid', async () => {
    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockResolvedValue()
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: undefined,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should return an error when there are no bookings for this offer', async () => {
    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        { body: { code: 'NO_BOOKING' }, status: 400 } as ApiResult,
        ''
      )
    )
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: 1,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Cette offre n’a aucune reservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
    )
  })

  it('should return a confirmation when the booking was cancelled', async () => {
    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockResolvedValue()
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: 1,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(notifySuccess).toHaveBeenNthCalledWith(
      1,
      'La réservation sur cette offre a été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.',
      { duration: NOTIFICATION_LONG_SHOW_DURATION }
    )

    expect(
      screen.queryByRole('button', { name: 'Confirmer' })
    ).not.toBeInTheDocument()
  })

  it('should return an error when booking cancellation failed', async () => {
    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockRejectedValueOnce({})
    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: 1,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la préréservation' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Une erreur est survenue lors de l’annulation de la réservation.',
      { duration: NOTIFICATION_LONG_SHOW_DURATION }
    )
  })


  it('should show cancel button when ENABLE_COLLECTIVE_NEW_STATUSES is on and offer has CAN_CANCEL allowed action', async () => {
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_CANCEL],
      id: 1,
    })
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: 1,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: false,
    },['ENABLE_COLLECTIVE_NEW_STATUSES'])

    expect(await screen.findByText('Annuler la préréservation')).toBeInTheDocument()
  })

  it('should not show cancel button when ENABLE_COLLECTIVE_NEW_STATUSES is and offer has not CAN_CANCEL allowed action', async () => {
    const offer = getCollectiveOfferFactory({
      allowedActions: [],
      id: 1,
    })
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

    const bookingRecap = collectiveBookingFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
      stock: collectiveBookingCollectiveStockFactory({
        offerId: 1,
      }),
    })

    renderCollectiveActionButtons({
      bookingRecap,
      isCancellable: false,
    },['ENABLE_COLLECTIVE_NEW_STATUSES'])

    await waitFor(() => {
      expect(screen.queryByText('Annuler la préréservation')).not.toBeInTheDocument()
    })
  })

})
