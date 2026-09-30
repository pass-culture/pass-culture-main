import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PriceCategoriesSection } from './PriceCategoriesSection'

describe('IndividualOfferSummary:PriceCategoriesSection', () => {
  it('should render without accessibility violations', async () => {
    const offer = getIndividualOfferFactory()
    const { container } = renderWithProviders(
      <PriceCategoriesSection offer={offer} canBeDuo shouldShowDivider />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render correctly', () => {
    const offer = getIndividualOfferFactory()

    renderWithProviders(
      <PriceCategoriesSection offer={offer} canBeDuo shouldShowDivider />
    )

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.getByText(/Accepter les réservations "Duo"/)
    ).toBeInTheDocument()
  })

  it('should render correctly when offer cannot be duo', () => {
    const offer = getIndividualOfferFactory()

    renderWithProviders(
      <PriceCategoriesSection
        offer={offer}
        canBeDuo={false}
        shouldShowDivider
      />
    )

    expect(screen.getByText(/Tarifs/)).toBeInTheDocument()
    expect(
      screen.queryByText(/Accepter les réservations "Duo"/)
    ).not.toBeInTheDocument()
  })
})
