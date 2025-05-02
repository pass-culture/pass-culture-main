import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes , Link } from 'react-router'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'

import { useFocus } from '../useFocus'

const FocusTopPageOrBackToNavLink = (): null => {
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
            <span>Main page</span>
            <Link to="/page-without-back-to-nav">
              Page Without "Back to Nav" link
            </Link>
            <Link to="/page-with-back-to-nav">
              Page With "Back to Nav" link
            </Link>
          </>
        }
      />
      <Route
        path="/page-without-back-to-nav"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <SkipLinks />
            <span>Page Without "Back to Nav" link</span>
          </>
        }
      />
      <Route
        path="/page-with-back-to-nav"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <SkipLinks />
            <a id="back-to-nav-link" href="#" />
            <span>Page With "Back to Nav" link</span>
          </>
        }
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )
}

describe('useFocus', () => {
  it('should focus on back to nav link when user navigates to another page', async () => {
    renderUseFocusRoutes()
    await userEvent.click(
      screen.getByRole('link', { name: 'Page With "Back to Nav" link' })
    )

    expect(document.activeElement?.id).toEqual('back-to-nav-link')
    await userEvent.tab()
    expect(document.activeElement?.id).not.toEqual('back-to-nav-link')
  })

  it('should focus on top of the page as a fallback', async () => {
    renderUseFocusRoutes()
    await userEvent.click(
      screen.getByRole('link', { name: 'Page Without "Back to Nav" link' })
    )

    expect(document.activeElement?.id).toEqual('unaccessible-top-page')
    await userEvent.tab()
    expect(document.activeElement?.id).not.toEqual('unaccessible-top-page')
  })
})
