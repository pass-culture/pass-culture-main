import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component } from './NonAttached'

const mockNavigate = vi.fn()

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: () => mockNavigate,
}))

describe('NonAttachedBanner', () => {
  it('should render a back button if FF is activated', async () => {
    renderWithProviders(<Component />, {
      features: ['WIP_SWITCH_VENUE'],
    })

    const retourBtn = screen.getByText('Retour vers la sélection du partenaire')
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith('/hub')
  })
})
