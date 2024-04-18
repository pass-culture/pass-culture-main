import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Footer from '../Footer'

const renderFooter = (
  isConnected: boolean = true,
  hasNewNav: boolean = false
) => {
  const storeOverrides = {
    user: {
      currentUser: isConnected
        ? {
            isAdmin: false,
            hasSeenProTutorials: true,
            navState: {
              newNavDate: hasNewNav ? '2021-01-01' : null,
            },
          }
        : null,
      initialized: true,
    },
  }
  renderWithProviders(<Footer />, {
    storeOverrides: storeOverrides,
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

  it('should not render sitemap if user is not connected', () => {
    renderFooter(false)

    expect(
      screen.queryByRole('link', { name: 'Plan du site' })
    ).not.toBeInTheDocument()
  })
})
