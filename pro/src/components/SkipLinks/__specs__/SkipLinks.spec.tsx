import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SkipLinksProvider } from '@/components/SkipLinks/SkipLinksContext'

import { SkipLinks } from '../SkipLinks'

const renderApp = () =>
  renderWithProviders(
    <Routes>
      <Route
        element={
          <SkipLinksProvider>
            <SkipLinks />
            <div id={'content'}>
              <a href="#">focusable content element</a>
            </div>
          </SkipLinksProvider>
        }
        path={'/accueil'}
      />
    </Routes>,
    { initialRouterEntries: ['/accueil'] }
  )

describe('SkipLinks', () => {
  it('should render', () => {
    renderApp()
    expect(screen.queryByText('Aller au contenu')).toBeInTheDocument()
    expect(screen.queryByText('Menu')).not.toBeInTheDocument()
  })
})
