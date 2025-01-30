import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { Footer } from './Footer'

const renderFooter = (isConnected: boolean = true) => {
  renderWithProviders(<Footer />, {
    user: isConnected
      ? sharedCurrentUserFactory({
          isAdmin: false,
          hasSeenProTutorials: true,
        })
      : null,
  })
}

describe('Footer', () => {
  it('should  render footer', () => {
    renderFooter(true)

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

  it('should render footer accessibility link', () => {
    renderFooter(true)

    expect(
      screen.queryByRole('link', { name: 'Accessibilité : non conforme' })
    ).toBeInTheDocument()
  })
})
