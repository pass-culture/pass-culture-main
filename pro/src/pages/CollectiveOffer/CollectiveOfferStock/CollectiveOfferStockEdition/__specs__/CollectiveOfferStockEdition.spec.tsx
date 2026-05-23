import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { apiNew } from '@/apiClient/api'
import { ApiError } from '@/apiClient/compat'
import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { CollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferStockEdition } from '../CollectiveOfferStockEdition'

const mockSyncVenue = vi.fn()
const mockSnackBarSuccess = vi.fn()
const mockSnackBarError = vi.fn()

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenue: mockSyncVenue }),
}))

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: mockSnackBarSuccess,
    error: mockSnackBarError,
  }),
}))

const renderCollectiveStockEdition = (
  path: string,
  props: CollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferStockEdition {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          allowedOnAdage: true,
        }),
      },
    },
  })
}

describe('CollectiveOfferStockEdition', () => {
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })
  const defaultOffer = getCollectiveOfferFactory({
    venue: {
      ...venue,
      managingOfferer: { ...offerer, siren: '123456789' },
      departementCode: '33',
      imgUrl: null,
    },
    allowedActions: [
      CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
    ],
  })

  it('should render in EDITION mode when stock is editable', async () => {
    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: defaultOffer,
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    expect(submitButton).toBeEnabled()
  })

  it('should render in READ_ONLY mode when stock is not editable', async () => {
    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: getCollectiveOfferFactory({
        ...defaultOffer,
        allowedActions: [],
      }),
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    expect(submitButton).toBeDisabled()
  })

  it('should call editCollectiveStock and show success on submit', async () => {
    vi.spyOn(apiNew, 'editCollectiveStock').mockResolvedValueOnce({} as any)

    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: defaultOffer,
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(apiNew.editCollectiveStock).toHaveBeenCalledTimes(1)
    })

    await waitFor(() => {
      expect(mockSnackBarSuccess).toHaveBeenCalledWith(
        'Vos modifications ont bien été enregistrées'
      )
    })
    expect(mockNavigate).toHaveBeenCalled()
    expect(mockSyncVenue).toHaveBeenCalledWith(defaultOffer.venue.id)
  })

  it('should display field errors on API error with status 400', async () => {
    const error = new ApiError('', 400, 'Bad Request', {
      totalPrice: ['Le prix est invalide'],
    })
    vi.spyOn(apiNew, 'editCollectiveStock').mockRejectedValueOnce(error)

    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: defaultOffer,
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Le prix est invalide')).toBeInTheDocument()
    })

    expect(mockSnackBarSuccess).not.toHaveBeenCalled()
    expect(mockSnackBarError).not.toHaveBeenCalled()
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('should show generic error on API error with status 500', async () => {
    vi.spyOn(apiNew, 'editCollectiveStock').mockRejectedValueOnce(
      new ApiError('', 500, 'Internal Server Error', {})
    )

    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: defaultOffer,
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(mockSnackBarError).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la mise à jour de votre stock.'
      )
    })

    expect(mockSnackBarSuccess).not.toHaveBeenCalled()
    expect(mockNavigate).not.toHaveBeenCalled()
  })
})
