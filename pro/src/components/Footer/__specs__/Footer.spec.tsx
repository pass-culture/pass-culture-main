import { screen } from '@testing-library/react'

import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import Footer from '../Footer'

const renderFooter = (
  isConnected: boolean = true,
  options?: RenderWithProvidersOptions
) => {
  const storeOverrides = {
    user: {
      currentUser: isConnected
        ? {
            isAdmin: false,
            hasSeenProTutorials: true,
          }
        : null,
      initialized: true,
    },
  }
  renderWithProviders(<Footer />, {
    storeOverrides: storeOverrides,
    ...options,
  })
}

describe('Footer', () => {
  it('should  render footer if ff is active', () => {
    renderFooter(true, {
      features: ['WIP_ENABLE_PRO_SIDE_NAV'],
    })

    expect(
      screen.queryByRole('link', { name: 'CGU professionnels' })
    ).toBeInTheDocument()
  })

  it('should not render footer if ff is not active', () => {
    renderFooter()

    expect(
      screen.queryByRole('link', { name: 'CGU professionnels' })
    ).not.toBeInTheDocument()
  })

  it('should not render sitemap if user is not connected', () => {
    renderFooter(false, {
      features: ['WIP_ENABLE_PRO_SIDE_NAV'],
    })

    expect(
      screen.queryByRole('link', { name: 'Plan du site' })
    ).not.toBeInTheDocument()
  })
})
