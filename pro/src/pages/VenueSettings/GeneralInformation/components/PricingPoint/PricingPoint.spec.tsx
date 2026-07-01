import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PricingPoint, type PricingPointProps } from './PricingPoint'

describe('PricingPoint', () => {
  const defaultProps: PricingPointProps = {
    venuePricingPoint: {
      id: 2,
      siret: '12345678900002',
      venueName: 'Nom de la structure de référence',
    },
  }

  it('should display a disabled select with venue pricing point info', () => {
    renderWithProviders(<PricingPoint {...defaultProps} />)

    const select = screen.getByRole('combobox', {
      name: /Structure avec SIRET utilisée pour le calcul de votre barème de remboursement/,
    })
    expect(select).toBeDisabled()
    expect(select).toHaveValue('2')
    expect(select).toHaveTextContent(
      'Nom de la structure de référence - 12345678900002'
    )
  })
})
