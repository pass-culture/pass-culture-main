import { screen } from '@testing-library/react'
import { vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Header } from './Header'

const defaultProps = {
  lateralPanelOpen: false,
  setLateralPanelOpen: vi.fn(),
  focusCloseButton: vi.fn(),
  disableHomeLink: false,
  adminArea: false,
}

describe('Header', () => {
  it('should show "Espace administration" button when FF is enabled and adminArea is false', () => {
    renderWithProviders(<Header {...defaultProps} />, {
      features: ['WIP_SWITCH_VENUE'],
    })
    expect(
      screen.getByRole('link', { name: 'Espace administration' })
    ).toHaveAttribute('href', '/remboursements')
  })

  it('should show "Revenir à l’Espace Partenaire" button when FF is enabled and adminArea is true', () => {
    renderWithProviders(<Header {...defaultProps} adminArea={true} />, {
      features: ['WIP_SWITCH_VENUE'],
    })
    expect(
      screen.getByRole('link', { name: 'Revenir à l’Espace Partenaire' })
    ).toHaveAttribute('href', '/accueil')
  })
})
