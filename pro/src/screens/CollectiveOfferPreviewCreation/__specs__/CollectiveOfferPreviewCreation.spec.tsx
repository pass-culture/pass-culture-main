import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { getCollectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import CollectiveOfferPreviewCreationScreen, {
  CollectiveOfferSummaryCreationProps,
} from '../CollectiveOfferPreviewCreation'

vi.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: vi.fn(),
}))

const renderCollectiveOfferPreviewCreation = (
  props: CollectiveOfferSummaryCreationProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferPreviewCreationScreen {...props} />, {
    ...options,
  })
}

const defaultProps = {
  offer: getCollectiveOfferTemplateFactory(),
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
  isTemplate: true,
}

describe('CollectiveOfferConfirmation', () => {
  const mockNotifyError = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.default>
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
    }))
  })

  it('should render selection duplication page', () => {
    renderCollectiveOfferPreviewCreation(defaultProps)

    expect(
      screen.getByRole('heading', {
        name: 'aperçu',
      })
    ).toBeInTheDocument()
  })

  it('should redirect to next step on submit', async () => {
    vi.spyOn(api, 'patchCollectiveOfferTemplatePublication').mockResolvedValue(
      defaultProps.offer
    )

    renderCollectiveOfferPreviewCreation(defaultProps)

    const nextStep = screen.getByText('Publier l’offre')

    await userEvent.click(nextStep)

    expect(api.patchCollectiveOfferTemplatePublication).toHaveBeenCalled()
  })

  it('should not redirect to next step on submit and show notification error', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOfferTemplatePublication'
    ).mockRejectedValueOnce('error')

    renderCollectiveOfferPreviewCreation(defaultProps)

    const nextStep = screen.getByText('Publier l’offre')

    await userEvent.click(nextStep)

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la publication de votre offre.'
    )
  })

  it('should redirect to preview step on click', async () => {
    renderCollectiveOfferPreviewCreation(defaultProps)

    const previewStep = screen.getByText('Étape précédente')

    await userEvent.click(previewStep)

    expect(previewStep.getAttribute('href')).toBe(
      `/offre/${defaultProps.offer.id}/collectif/vitrine/creation/recapitulatif`
    )
  })
})
