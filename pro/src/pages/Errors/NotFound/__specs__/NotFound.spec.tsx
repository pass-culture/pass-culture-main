import { screen } from '@testing-library/react'
import * as router from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NotFound } from '../NotFound'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: () => ({ state: {} }),
}))

describe('NotFound', () => {
  it('should display a message notifying the user they are on a wrong path', () => {
    renderWithProviders(<NotFound />)

    expect(screen.getByText('Cette page n’existe pas.')).toBeInTheDocument()
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
