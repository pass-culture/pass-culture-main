import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ProductBanner } from './ProductBanner'

describe('IndividualOffer::ProductBanner', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<ProductBanner />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the product-based warning banner', () => {
    renderWithProviders(<ProductBanner />)

    expect(
      screen.getByText(
        'Des informations proviennent d’un EAN et ne peuvent pas être modifiées depuis l’espace partenaire'
      )
    ).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
