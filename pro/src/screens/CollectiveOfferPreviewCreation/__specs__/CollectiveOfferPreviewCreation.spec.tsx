import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { sub } from 'date-fns'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import {
  defaultGetVenue,
  getCollectiveOfferCollectiveStockFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import {
  CollectiveOfferPreviewCreationScreen,
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
  isTemplate: true,
  offerer: defaultGetOffererResponseModel,
}

describe('CollectiveOfferConfirmation', () => {
  const mockNotifyError = vi.fn()
  const mockNotifySuccess = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
      success: mockNotifySuccess,
    }))

    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)
  })

  it('should render selection duplication page', async () => {
    renderCollectiveOfferPreviewCreation(defaultProps)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: defaultProps.offer.name,
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

    const previewStep = screen.getByText('Retour')

    await userEvent.click(previewStep)

    expect(previewStep.getAttribute('href')).toBe(
      `/offre/${defaultProps.offer.id}/collectif/vitrine/creation/recapitulatif`
    )
  })

  it('should redirect to list offer with success notification', async () => {
    renderCollectiveOfferPreviewCreation(defaultProps, {
      features: ['WIP_ENABLE_COLLECTIVE_DRAFT_OFFERS'],
    })

    const saveAndQuitButton = screen.getByText(
      'Sauvegarder le brouillon et quitter'
    )

    expect(saveAndQuitButton.getAttribute('href')).toBe('/offres/collectives')

    await userEvent.click(saveAndQuitButton)

    expect(mockNotifySuccess).toHaveBeenCalledWith(
      'Brouillon sauvegardé dans la liste des offres'
    )
  })

  it('should notify of an error if the offer booking limit date is in the past', async () => {
    const offer = getCollectiveOfferFactory()
    const yesterday = sub(new Date(), { days: 1 }).toISOString()
    offer.collectiveStock = getCollectiveOfferCollectiveStockFactory({
      bookingLimitDatetime: yesterday,
    })
    renderCollectiveOfferPreviewCreation({
      ...defaultProps,
      offer: offer,
    })

    const nextStep = screen.getByText('Publier l’offre')
    await userEvent.click(nextStep)

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Les dates de limite de réservation ou d’évènement doivent être égales ou postérieures à la date actuelle.'
    )
  })

  it('should notify of an error if the offer beginning date is in the past', async () => {
    const offer = getCollectiveOfferFactory()
    const yesterday = sub(new Date(), { days: 1 }).toISOString()
    offer.collectiveStock = getCollectiveOfferCollectiveStockFactory({
      startDatetime: yesterday,
    })
    renderCollectiveOfferPreviewCreation({
      ...defaultProps,
      offer: offer,
    })

    const nextStep = screen.getByText('Publier l’offre')
    await userEvent.click(nextStep)

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Les dates de limite de réservation ou d’évènement doivent être égales ou postérieures à la date actuelle.'
    )
  })
})
