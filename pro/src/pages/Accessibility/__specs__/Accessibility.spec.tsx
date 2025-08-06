import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AccessibilityMenu } from '../AccessibilityMenu'

describe('Statement of Accessibility page', () => {
  it('should display Accessibility information message', () => {
    renderWithProviders(<AccessibilityMenu />)
    expect(screen.getByText('Informations d’accessibilité')).toBeInTheDocument()
  })
})
