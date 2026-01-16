import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { CollectiveOfferTemplateAllowedAction } from '@/apiClient/v1'
import { GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Mode } from '@/commons/core/OfferEducational/types'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferEducationalActions,
  type OfferEducationalActionsProps,
} from '../OfferEducationalActions'

vi.mock('@/apiClient/api', () => ({
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
  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()

  beforeEach(async () => {
    vi.resetAllMocks()
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
      success: snackBarSuccess,
    }))
  })

  it('should update active status value for template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory({
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
    await waitFor(() => expect(snackBarError).toHaveBeenCalledTimes(1))
  })

  it('should show error notification with error message when activation fails with Error instance', async () => {
    const errorMessage = 'Erreur réseau'
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue(new Error(errorMessage))

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier',
    })

    await userEvent.click(activateOffer)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        `Une erreur est survenue lors de l’activation de votre offre. ${errorMessage}`
      )
    })
  })

  it('should show error notification with error message when deactivation fails with Error instance', async () => {
    const errorMessage = 'Erreur serveur'
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue(new Error(errorMessage))

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })
    const deactivateOffer = screen.getByRole('button', {
      name: 'Mettre en pause',
    })

    await userEvent.click(deactivateOffer)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        `Une erreur est survenue lors de la désactivation de votre offre. ${errorMessage}`
      )
    })
  })

  it('should show error notification without error message when activation fails with non-Error instance', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue({ isOk: false, code: 500 })

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
      }),
    })
    const activateOffer = screen.getByRole('button', {
      name: 'Publier',
    })

    await userEvent.click(activateOffer)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        `Une  erreur est survenue lors de l’activation de votre offre.`
      )
    })
  })

  it('should show error notification without error message when deactivation fails with non-Error instance', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValue({ isOk: false, code: 500 })

    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })
    const deactivateOffer = screen.getByRole('button', {
      name: 'Mettre en pause',
    })

    await userEvent.click(deactivateOffer)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(
        `Une  erreur est survenue lors de la désactivation de votre offre.`
      )
    })
  })

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions({
      ...defaultValues,
      offer: getCollectiveOfferTemplateFactory({
        isTemplate: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })
    expect(
      screen.getByRole('button', { name: 'Mettre en pause' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
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

    expect(snackBarSuccess).toHaveBeenCalledWith(
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

    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre offre est mise en pause et n’est plus visible sur ADAGE'
    )
  })
})
