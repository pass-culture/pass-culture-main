import { screen } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'

import SkipLinks from '../SkipLinks'

const renderApp = ({ displayMenu }: { displayMenu?: boolean }) =>
  renderWithProviders(
    <Routes>
      <Route
        element={
          <div>
            <SkipLinks displayMenu={displayMenu} />
            <div id="header-navigation">
              <a href="#">first focusable content element</a>
            </div>
            <div id="content">
              <a href="#">second focusable content element</a>
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
    renderApp({})
    expect(screen.queryByText('Aller au contenu')).toBeInTheDocument()
    expect(screen.queryByText('Menu')).not.toBeInTheDocument()
  })

  it('should display menu', () => {
    renderApp({ displayMenu: true })
    expect(screen.queryByText('Menu')).toBeInTheDocument()
  })
})
