import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { Link } from 'react-router-dom'

import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import { renderWithProviders } from 'utils/renderWithProviders'

import { useFocus } from '../useFocus'

const FocusTopPage = (): null => {
  useFocus()
  return null
}

const renderUseFocusRoutes = (url = '/accueil') => {
  renderWithProviders(
    <Routes>
      <Route
        path="/accueil"
        element={
          <>
            <SkipLinks />
            <span>Main page</span>
            <Link to="/guichet">Guichet</Link>
          </>
        }
      />
      <Route
        path="/guichet"
        element={
          <>
            <FocusTopPage />
            <SkipLinks />
            <span>Guichet page</span>
          </>
        }
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )
}

describe('useFocus', () => {
  it('should focus on top of the page when user navigates to another page', async () => {
    renderUseFocusRoutes()
    await userEvent.click(screen.getByRole('link', { name: 'Guichet' }))
    expect(document.activeElement?.id).toEqual('top-page')
    await userEvent.tab()
    expect(document.activeElement?.id).not.toEqual('top-page')
  })
})
