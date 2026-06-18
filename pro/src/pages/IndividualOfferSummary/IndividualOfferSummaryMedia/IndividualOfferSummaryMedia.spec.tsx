import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryMedia } from './IndividualOfferSummaryMedia'

const renderIndividualOfferSummaryScreen = () => {
  const contextValue = individualOfferContextValuesFactory()

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferSummaryMedia />
    </IndividualOfferContext.Provider>,
    {
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )
}

const waitForRecommendationCardFetch = async () => {
  await waitFor(() => {
    expect(api.getOfferProAdvice).toHaveBeenCalled()
  })
}

const LABELS = {
  mediaSectionTitle: 'Image et vidéo',
  actionBarLinkLabel: 'Retour à la liste des offres',
}

describe('IndividualOfferSummaryMedia', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: null,
    })
  })

  it('should render a media section', async () => {
    renderIndividualOfferSummaryScreen()
    await waitForRecommendationCardFetch()

    const mediaSection = screen.getByRole('heading', {
      name: LABELS.mediaSectionTitle,
    })
    expect(mediaSection).toBeInTheDocument()
  })

  it('should render an action bar & back to offers list button', async () => {
    renderIndividualOfferSummaryScreen()
    await waitForRecommendationCardFetch()

    const actionBarLink = screen.getByRole('link', {
      name: LABELS.actionBarLinkLabel,
    })
    expect(actionBarLink).toBeInTheDocument()
  })
})
