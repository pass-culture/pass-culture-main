import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/compat'
import { CollectiveOfferAllowedAction } from '@/apiClient/v1'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { CollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferStockForm } from '../components/CollectiveOfferStockForm/CollectiveOfferStockForm'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'
import { CollectiveOfferStockEdition } from './CollectiveOfferStockEdition'

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

vi.mock(
  '../components/CollectiveOfferStockForm/CollectiveOfferStockForm',
  () => ({
    CollectiveOfferStockForm: vi.fn(),
  })
)

vi.mock('../components/OfferEducationalStock/OfferEducationalStock', () => ({
  OfferEducationalStock: vi.fn(),
}))

const renderCollectiveStockEdition = (
  path: string,
  props: CollectiveOfferFromParamsProps,
  features: string[] = []
) => {
  renderWithProviders(<CollectiveOfferStockEdition {...props} />, {
    initialRouterEntries: [path],
    features,
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

  beforeEach(async () => {
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)

    const actualOld = await vi.importActual<
      typeof import('../components/OfferEducationalStock/OfferEducationalStock')
    >('../components/OfferEducationalStock/OfferEducationalStock')
    vi.mocked(OfferEducationalStock).mockImplementation(
      actualOld.OfferEducationalStock
    )

    const actualNew = await vi.importActual<
      typeof import('../components/CollectiveOfferStockForm/CollectiveOfferStockForm')
    >('../components/CollectiveOfferStockForm/CollectiveOfferStockForm')
    vi.mocked(CollectiveOfferStockForm).mockImplementation(
      actualNew.CollectiveOfferStockForm
    )
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
    vi.spyOn(api, 'editCollectiveStock').mockResolvedValueOnce({} as any)

    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: defaultOffer,
    })

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.editCollectiveStock).toHaveBeenCalledTimes(1)
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
      price: ['Le prix est invalide'],
    })
    vi.spyOn(api, 'editCollectiveStock').mockRejectedValueOnce(error)

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
    vi.spyOn(api, 'editCollectiveStock').mockRejectedValueOnce(
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

  it('should render for offer imported with a public api', async () => {
    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      offer: { ...defaultOffer, isPublicApi: true },
    })

    expect(
      await screen.findByText(
        'Cette offre a été importée automatiquement depuis votre système de billetterie.'
      )
    ).toBeVisible()
  })

  it('on submit with WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS enabled: should not send priceDetail on stock patch', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'editCollectiveStock').mockResolvedValueOnce({} as any)
    const formMock = vi.fn(({ onAfterSubmit }) => {
      const updatedStock = { numberOfTickets: 12, priceDetail: 'test' }
      return (
        <button onClick={() => onAfterSubmit(updatedStock)}>Enregistrer</button>
      )
    })
    vi.mocked(CollectiveOfferStockForm).mockImplementationOnce(formMock)
    vi.mocked(OfferEducationalStock).mockImplementationOnce(formMock)

    renderCollectiveStockEdition(
      '/offre/A1/collectif/stocks/edition',
      { offer: defaultOffer },
      ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS']
    )

    const submitButton = await screen.findByRole('button', {
      name: /Enregistrer/,
    })
    await user.click(submitButton)
    expect(api.editCollectiveStock).toHaveBeenCalledExactlyOnceWith({
      path: { collective_stock_id: defaultOffer.collectiveStock?.id },
      body: { numberOfTickets: 12 },
    })
  })
})
