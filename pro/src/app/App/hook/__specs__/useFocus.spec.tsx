import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Link, Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { BasicLayout } from '../../layouts/BasicLayout/BasicLayout'
import { SignUpLayout } from '../../layouts/logged-out/SignUpLayout/SignUpLayout'
import { useFocus } from '../useFocus'

// Avoid "document.getElementById(...).scrollTo is not a function" error.
Element.prototype.scrollTo = () => {}

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
            <FocusTopPageOrBackToNavLink />
            <BasicLayout mainHeading="Accueil">
              <Link to="/connection">Log Out</Link>
            </BasicLayout>
          </>
        }
      />
      <Route
        path="/connection"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <SignUpLayout mainHeading="Connexion">
              <Link to="/accueil">Log In</Link>
            </SignUpLayout>
          </>
        }
      />
    </Routes>,
    {
      initialRouterEntries: [url],
      storeOverrides: {
        offerer: {
          offererNamesAttached: [{ id: 456, name: 'Offerer' }],
        },
        user: {
          currentUser: { id: 123 },
        },
      },
    }
  )
}

describe('useFocus', () => {
  it('should always focus on top of the page after a navigation', async () => {
    renderUseFocusRoutes()

    expect(screen.getByRole('heading', { name: 'Accueil' })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('link', { name: 'Log Out' }))

    expect(screen.getByTestId('top-page')).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Aller au contenu' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Connexion' })
    ).toBeInTheDocument()

    expect(document.activeElement?.id).toEqual('top-page')

    await userEvent.tab()

    expect(document.activeElement?.id).toEqual('go-to-content')
  })
})
