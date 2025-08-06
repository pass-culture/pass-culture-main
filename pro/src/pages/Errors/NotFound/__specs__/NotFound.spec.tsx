import { screen } from '@testing-library/react'
import * as router from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NotFound } from '../NotFound'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: () => ({ state: {} }),
}))

describe('src | components | pages | NotFound', () => {
  it('should display a message notifying the user they are on a wrong path and add a link to home', () => {
    // when
    renderWithProviders(<NotFound />)
    // then
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Oh non !'
    )
    expect(screen.getByRole('link')).toHaveAttribute('href', '/accueil')
    expect(screen.getByText('Cette page n’existe pas.')).toBeInTheDocument()
  })

  it('should display a link with the redirect props url if not default', () => {
    // when
    const props = {
      redirect: '/mon/autre/url',
    }
    renderWithProviders(<NotFound {...props} />)

    // then
    expect(screen.getByRole('link')).toHaveAttribute('href', '/mon/autre/url')
  })

  it('should display a specific error message when an offer was not found', () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      state: { from: 'offer' },
    } as router.Location)

    renderWithProviders(<NotFound />)

    expect(
      screen.getByText('Cette offre n’existe pas ou a été supprimée.')
    ).toBeInTheDocument()
  })
})
