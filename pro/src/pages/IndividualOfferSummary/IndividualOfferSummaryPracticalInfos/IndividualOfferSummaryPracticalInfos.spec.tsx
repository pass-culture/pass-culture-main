import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryPracticalInfos } from './IndividualOfferSummaryPracticalInfos'

const renderIndividualOfferSummaryPracticalInfos = (
  context?: Partial<IndividualOfferContextValues>
) => {
  const contextValue = individualOfferContextValuesFactory()

  renderWithProviders(
    <IndividualOfferContext.Provider value={{ ...contextValue, ...context }}>
      <IndividualOfferSummaryPracticalInfos />
    </IndividualOfferContext.Provider>
  )
}

describe('IndividualOfferSummaryPracticalInfos', () => {
  it('should render a spinner if there is no offer', () => {
    renderIndividualOfferSummaryPracticalInfos({ offer: null })

    expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should render a practical info section', () => {
    renderIndividualOfferSummaryPracticalInfos()

    expect(
      screen.getByRole('heading', {
        name: 'Informations pratiques',
      })
    ).toBeInTheDocument()
  })
})
