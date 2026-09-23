import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Commitment } from '../Commitment'

describe('Statement of Commitment page', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<Commitment />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display Commitment information message', () => {
    renderWithProviders(<Commitment />)
    expect(
      screen.getByText(
        'Les engagements du pass Culture pour l’accessibilité numérique'
      )
    ).toBeInTheDocument()
  })
})
