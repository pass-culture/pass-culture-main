import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryPracticalInfos } from './IndividualOfferSummaryPracticalInfos'

const renderIndividualOfferSummaryPracticalInfos = (
  context?: Partial<IndividualOfferContextValues>
) => {
  const contextValue = individualOfferContextValuesFactory()

  renderWithProviders(
    <IndividualOfferContext.Provider value={{ ...contextValue, ...context }}>
      <IndividualOfferSummaryPracticalInfos />
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

describe('IndividualOfferSummaryPracticalInfos', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: null,
    })
  })

  it('should render a spinner if there is no offer', () => {
    renderIndividualOfferSummaryPracticalInfos({ offer: null })

    expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should render a practical info section', async () => {
    renderIndividualOfferSummaryPracticalInfos()
    await waitForRecommendationCardFetch()

    expect(
      screen.getByRole('heading', {
        name: 'Informations pratiques',
      })
    ).toBeInTheDocument()
  })
})
