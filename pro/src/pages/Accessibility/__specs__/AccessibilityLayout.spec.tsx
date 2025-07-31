import { screen } from '@testing-library/react'

import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  AccessibilityLayout,
  type AccessibilityLayoutProps,
} from '../AccessibilityLayout'

const renderAccessibilityLayout: RenderComponentFunction<
  AccessibilityLayoutProps
> = ({ options = {}, props = {} }) => {
  renderWithProviders(
    <AccessibilityLayout {...props}>Children</AccessibilityLayout>,
    options
  )
}

describe('Accessibility layout', () => {
  it('should handle connected users', () => {
    renderAccessibilityLayout({
      options: {
        storeOverrides: {
          offerer: currentOffererFactory(),
          user: { currentUser: sharedCurrentUserFactory() },
        },
      },
    })

    expect(screen.queryByTestId('logged-out-section')).not.toBeInTheDocument()

    expect(
      screen.queryByText('Retour à la page de connexion')
    ).not.toBeInTheDocument()
  })

  it('should handle not connected with back button', () => {
    renderAccessibilityLayout({ props: { showBackToSignInButton: true } })

    expect(screen.getByTestId('logged-out-section')).toBeInTheDocument()
    expect(
      screen.getByText('Retour à la page de connexion')
    ).toBeInTheDocument()
  })

  it('should handle not connected', () => {
    renderAccessibilityLayout({})

    expect(screen.getByTestId('logged-out-section')).toBeInTheDocument()
    expect(
      screen.queryByText('Retour à la page de connexion')
    ).not.toBeInTheDocument()
  })
})
