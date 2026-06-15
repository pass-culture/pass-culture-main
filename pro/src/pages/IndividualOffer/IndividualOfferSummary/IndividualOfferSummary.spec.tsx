import { screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import { apiNew } from '@/apiClient/api'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummary } from './IndividualOfferSummary'

vi.mock('./components/IndividualOfferSummaryScreen', () => ({
  IndividualOfferSummaryScreen: () => (
    <div data-testid="summary-screen">Summary Screen</div>
  ),
}))

const renderIndividualOfferSummary: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params) => {
  const contextValues: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...params.contextValues,
  }
  const user = sharedCurrentUserFactory()
  const options: RenderWithProvidersOptions = {
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
      },
    },
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummary />
    </IndividualOfferContext.Provider>,
    options
  )
}

const waitForRecommendationCardFetch = async () => {
  await waitFor(() => {
    expect(apiNew.getOfferProAdvice).toHaveBeenCalled()
  })
}

describe('<IndividualOfferSummary />', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: null,
    })
  })

  it('renders spinner when no offer in context', () => {
    const contextValues = {
      offer: null,
    }

    renderIndividualOfferSummary({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('renders summary screen when offer is in context', async () => {
    const contextValues = {
      offer: getIndividualOfferFactory(),
    }

    renderIndividualOfferSummary({ contextValues })
    await waitForRecommendationCardFetch()

    expect(screen.getByTestId('summary-screen')).toBeInTheDocument()
  })
})
