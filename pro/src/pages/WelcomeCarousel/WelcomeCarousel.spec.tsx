import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { WelcomeCarousel } from './WelcomeCarousel'

const renderWelcomeCarroussel = (initialPath: string = '/bienvenue') => {
  return renderWithProviders(<WelcomeCarousel />, {
    initialRouterEntries: [initialPath],
  })
}
describe('<WelcomeCarousel />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWelcomeCarroussel()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the right title and subtitle', () => {
    renderWelcomeCarroussel('/bienvenue/offres-scolaires')

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'Offres pour les groupes scolaires',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Intervenez auprès des classes',
      })
    ).toBeInTheDocument()
  })

  it('should display the buttons', () => {
    renderWelcomeCarroussel('/bienvenue/prochaines-etapes')

    expect(
      screen.getByRole('link', { name: 'Démarrer l’inscription' })
    ).toBeInTheDocument()
  })
})
