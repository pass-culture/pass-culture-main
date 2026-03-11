import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SkipLinksProvider } from '@/components/SkipLinks/SkipLinksContext'

import { SkipLinks } from '../SkipLinks/SkipLinks'
import { Footer } from './Footer'

const renderFooter = (isConnected: boolean = true) => {
  renderWithProviders(<Footer />, {
    user: isConnected
      ? sharedCurrentUserFactory({
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

  it('should render footer accessibility link', () => {
    renderFooter(true)

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

  it('should portal "go to footer" skip link when SkipLinks context provides a container', () => {
    renderWithProviders(
      <SkipLinksProvider>
        <SkipLinks />
        <Footer />
      </SkipLinksProvider>,
      {
        user: sharedCurrentUserFactory({ hasSeenProTutorials: true }),
      }
    )

    expect(
      screen.getByRole('link', { name: 'Aller au pied de page' })
    ).toBeInTheDocument()
  })
})
