import { screen } from '@testing-library/dom'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorEmailConfirmation } from './SimulatorEmailConfirmation'

describe('<SimulatorEmailConfirmation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorEmailConfirmation />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render title, subtitle and a CTA', () => {
    renderWithProviders(<SimulatorEmailConfirmation />)
    expect(screen.getByRole('heading', { level: 1 })).toBeVisible()
    expect(screen.getByRole('heading', { level: 2 })).toBeVisible()

    expect(
      screen.getByRole('link', { name: "Retour à l'inscription" })
    ).toHaveAttribute('href', '/inscription/preparation/resultats')
  })
})
