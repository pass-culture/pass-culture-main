import { screen, waitFor } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import {
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveOfferSummaryEdition } from './CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderCollectiveOfferSummaryEdition = (
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferSummaryEdition offer={offer} />, {
    user: sharedCurrentUserFactory(),
    ...options,
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          allowedOnAdage: true,
        }),
      },
      ...options?.storeOverrides,
    },
  })
}

describe('CollectiveOfferSummary', () => {
  let offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel

  it('should display hide offer option when action is allowed', async () => {
    offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
    })

    renderCollectiveOfferSummaryEdition(offer)

    const desactivateOffer = await screen.findByRole('button', {
      name: 'Mettre en pause',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should display bookable offer detail page when offer is bookable', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferFactory())

    expect(await screen.findByText('n°2')).toBeInTheDocument()
  })

  it('should not display bookable offer detail page when offer is template', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferTemplateFactory())

    await waitFor(() =>
      expect(screen.queryByText('n°2')).not.toBeInTheDocument()
    )
  })

  it('should have the correct url for the list button when offer isTemplate is true', async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
    })

    renderCollectiveOfferSummaryEdition(offer)

    const listButton = await screen.findByRole('link', {
      name: /Retour à la liste des offres/i,
    })
    expect(listButton).toHaveAttribute('href', '/offres/vitrines')
  })
})
