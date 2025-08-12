import { screen } from '@testing-library/react'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { EndBanner } from './EndBanner'

describe('EndBanner', () => {
  it('should show edit link when canEditDiscount is true', () => {
    renderWithProviders(<EndBanner offerId={123} canEditDiscount={true} />)

    const link = screen.getByText(
      "Modifier à la baisse le prix ou le nombre d'élèves"
    )

    expect(link).toHaveAttribute('href', '/offre/123/collectif/stocks/edition')
  })

  it('should not show edit link when canEditDiscount is true', () => {
    renderWithProviders(<EndBanner offerId={123} canEditDiscount={false} />)

    const link = screen.queryByText(
      "Modifier à la baisse le prix ou le nombre d'élèves"
    )

    expect(link).not.toBeInTheDocument()
  })
})
