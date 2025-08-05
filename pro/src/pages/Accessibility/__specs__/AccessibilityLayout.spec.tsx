import { screen } from '@testing-library/react'

import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { AccessibilityLayout } from 'pages/Accessibility/AccessibilityLayout'

describe('Accessibility layout', () => {
  it('should handle connected users', () => {
    const user = sharedCurrentUserFactory()
    renderWithProviders(<AccessibilityLayout>Children</AccessibilityLayout>, {
      user,
      storeOverrides: {
        user: {
          currentUser: user,
        },
        offerer: currentOffererFactory(),
      },
    })
    expect(screen.queryByTestId('logged-out-section')).not.toBeInTheDocument()

    expect(
      screen.queryByText('Retour à la page de connexion')
    ).not.toBeInTheDocument()
  })

  it('should handle not connected with back button', () => {
    renderWithProviders(
      <AccessibilityLayout showBackToSignInButton={true}>
        Children
      </AccessibilityLayout>
    )
    expect(screen.getByTestId('logged-out-section')).toBeInTheDocument()
    expect(
      screen.getByText('Retour à la page de connexion')
    ).toBeInTheDocument()
  })

  it('should handle not connected', () => {
    renderWithProviders(<AccessibilityLayout>Children</AccessibilityLayout>)
    expect(screen.getByTestId('logged-out-section')).toBeInTheDocument()
    expect(
      screen.queryByText('Retour à la page de connexion')
    ).not.toBeInTheDocument()
  })
})
