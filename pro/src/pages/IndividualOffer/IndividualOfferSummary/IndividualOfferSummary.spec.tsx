import { screen } from '@testing-library/react'
import { vi } from 'vitest'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
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
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummary />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferSummary />', () => {
  it('renders spinner when no offer in context', () => {
    const contextValues = {
      offer: null,
    }

    renderIndividualOfferSummary({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('renders summary screen when offer is in context', () => {
    const contextValues = {
      offer: getIndividualOfferFactory(),
    }

    renderIndividualOfferSummary({ contextValues })

    expect(screen.getByTestId('summary-screen')).toBeInTheDocument()
  })
})
