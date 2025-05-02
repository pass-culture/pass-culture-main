import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { SkipLinks } from '../SkipLinks'

const renderApp = () =>
  renderWithProviders(
    <Routes>
      <Route
        element={
          <div>
            <SkipLinks />
            <div id="content">
              <a href="#">focusable content element</a>
            </div>
          </div>
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
