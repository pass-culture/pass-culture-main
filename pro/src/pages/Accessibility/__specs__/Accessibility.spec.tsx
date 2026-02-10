import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { AccessibilityMenu } from '../AccessibilityMenu'

const renderAccessibilityMenu: RenderComponentFunction = () =>
  renderWithProviders(<AccessibilityMenu />)

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
  it('should display the back button and return to previous page on click', async () => {
    renderAccessibilityMenu({})

    const retourBtn = screen.getByText('Retour')
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledTimes(1)
  })
})
