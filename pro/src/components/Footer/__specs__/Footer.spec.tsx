import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Footer } from '../Footer'

const renderFooter = (
  isConnected: boolean = true,
  hasNewNav: boolean = false
) => {
  renderWithProviders(<Footer />, {
    user: isConnected
      ? sharedCurrentUserFactory({
          isAdmin: false,
          hasSeenProTutorials: true,
          navState: {
            newNavDate: hasNewNav ? '2021-01-01' : null,
          },
        })
      : null,
  })
}

describe('Footer', () => {
  it('should  render footer', () => {
    renderFooter(true, true)

    expect(
      screen.queryByRole('link', { name: /CGU professionnels/ })
    ).toBeInTheDocument()
  })

  it('should not render footer if ff is not active', () => {
    renderFooter()

    expect(
      screen.queryByRole('link', { name: 'CGU professionnels' })
    ).not.toBeInTheDocument()
  })

  it('should render footer accessibility link when the user has the new nav', () => {
    renderFooter(true, true)

    expect(
      screen.queryByRole('link', { name: 'Accessibilité : non conforme' })
    ).toBeInTheDocument()
  })

  it('should not render sitemap if user is not connected', () => {
    renderFooter(false)

    expect(
      screen.queryByRole('link', { name: 'Plan du site' })
    ).not.toBeInTheDocument()
  })
})
