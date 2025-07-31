import { screen } from '@testing-library/react'

import {
  RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { AccessibilityMenu } from '../AccessibilityMenu'

const renderAccessibilityMenu: RenderComponentFunction = () => {
  renderWithProviders(<AccessibilityMenu />)
}

describe('Statement of Accessibility page', () => {
  it('should display Accessibility information message', () => {
    renderAccessibilityMenu({})

    expect(screen.getByText('Informations d’accessibilité')).toBeInTheDocument()
  })
})
