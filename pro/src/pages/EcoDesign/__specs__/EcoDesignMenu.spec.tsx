import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { EcoDesignMenu } from '../EcoDesignMenu'

const renderEcoDesignMenu: RenderComponentFunction = ({ options = {} }) =>
  renderWithProviders(<EcoDesignMenu />, options)

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

describe('Statement of EcoDesign page', () => {
  it('should display EcoDesign information message', () => {
    renderEcoDesignMenu({})

    expect(
      screen.getByText("Déclaration d'écoconception de l'espace partenaires")
    ).toBeVisible()
  })

  it('should display the back button and return to home on click if logged in', async () => {
    renderEcoDesignMenu({
      options: {
        storeOverrides: {
          user: { currentUser: { id: 123 } },
        },
      },
    })

    const retourBtn = screen.getByText('Retour')
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith('/accueil')
  })

  it('should display the back button and return to connexion page on click if logged out', async () => {
    renderEcoDesignMenu({
      options: {
        storeOverrides: {
          user: { currentUser: null },
        },
      },
    })

    const retourBtn = screen.getByText('Retour')
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith('/connexion')
  })
})
