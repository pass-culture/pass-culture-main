import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ReimbursementFields,
  type ReimbursementFieldsProps,
} from '../ReimbursementFields'

describe('ReimbursementFields', () => {
  const defaultProps: ReimbursementFieldsProps = {
    venuePricingPoint: {
      id: 1,
      siret: '12345678900001',
      venueName: 'Mon Lieu',
    },
  }

  it('should display the reimbursement section title', () => {
    renderWithProviders(<ReimbursementFields {...defaultProps} />)

    expect(
      screen.getByRole('heading', { name: /Barème de remboursement/ })
    ).toBeInTheDocument()
  })

  it('should display the pricing point select', () => {
    renderWithProviders(<ReimbursementFields {...defaultProps} />)

    expect(
      screen.getByText(
        /Structure avec SIRET utilisée pour le calcul de votre barème de remboursement/
      )
    ).toBeInTheDocument()
  })
})
