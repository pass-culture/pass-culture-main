import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { AccessibilityMenu } from '../AccessibilityMenu'

const renderAccessibilityMenu: RenderComponentFunction = ({ options = {} }) =>
  renderWithProviders(<AccessibilityMenu />, options)

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

describe('Statement of Accessibility page', () => {
  it('should display Accessibility information message', () => {
    renderAccessibilityMenu({})

    expect(screen.getByText('Informations d’accessibilité')).toBeInTheDocument()
  })
  it('should display the back button and return to home on click if logged in', async () => {
    renderAccessibilityMenu({
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
    renderAccessibilityMenu({
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
