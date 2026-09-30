import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Declaration } from '../Declaration'

describe('Statement of Declaration page', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<Declaration />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display Declaration information message', () => {
    renderWithProviders(<Declaration />)
    expect(screen.getByText(/Déclaration d’accessibilité/)).toBeInTheDocument()
  })
})
