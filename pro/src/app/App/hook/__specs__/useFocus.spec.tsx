import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { Link } from 'react-router-dom'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import { BackToNavLink } from 'components/BackToNavLink/BackToNavLink'

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
              Go to Page Without "Back to Nav" link
            </Link>
            <Link to="/page-with-back-to-nav">
              Go to Page With "Back to Nav" link
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
            <BackToNavLink />
            <span>Page With "Back to Nav" link</span>
          </>
        }
      />
    </Routes>,
    { initialRouterEntries: [url] }
  )
}

describe('useFocus', () => {
  it('should focus on back to nav link when user navigates to another page and the link exists', async () => {
    renderUseFocusRoutes('/accueil')

    await waitFor(async () => {
      console.log('user navigates to another page and the link exists')
      const goToPageWithBackToNavLink = screen.getByRole('link', {
        name: 'Go to Page With "Back to Nav" link',
      })

      await userEvent.click(goToPageWithBackToNavLink)
    })

    await waitFor(async () => {
      const backToNavLink = screen.getByRole('link', {
        name: 'Revenir à la barre de navigation',
      })
      expect(backToNavLink).toBeInTheDocument()
      expect(document.activeElement?.id).toEqual('back-to-nav-link')
      await userEvent.tab()
      expect(document.activeElement?.id).not.toEqual('back-to-nav-link')
    })
  })

  it('should focus on top of the page as a fallback', async () => {
    renderUseFocusRoutes()
    await userEvent.click(
      screen.getByRole('link', { name: 'Go to Page Without "Back to Nav" link' })
    )

    await waitFor(async () => {
      const topPageLink = screen.getByTestId('top-page')
      expect(topPageLink).toBeInTheDocument()
      expect(document.activeElement?.id).toEqual('top-page')
      await userEvent.tab()
      expect(document.activeElement?.id).not.toEqual('top-page')
    })
  })

  it('should focus on top of the page when the page is refreshed', async () => {
    renderUseFocusRoutes('/page-with-back-to-nav')

    await waitFor(async () => {
      const topPageLink = screen.getByTestId('top-page')
      expect(topPageLink).toBeInTheDocument()
      expect(document.activeElement?.id).toEqual('top-page')
      await userEvent.tab()
      expect(document.activeElement?.id).not.toEqual('top-page')
    })
  })
})
