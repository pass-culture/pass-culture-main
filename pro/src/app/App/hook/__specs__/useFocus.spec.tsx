import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Link, Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'
import { Stepper } from '@/components/Stepper/Stepper'

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
        path="/offre/individuelle/creation"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <BasicLayout mainHeading="Créer une offre individuelle">
              <Stepper
                activeStep="details"
                steps={[
                  {
                    id: 'details',
                    label: 'Détails',
                    url: '/offre/individuelle/creation',
                  },
                  {
                    id: 'informations-pratiques',
                    label: 'Informations pratiques',
                    url: '/offre/individuelle/creation/informations-pratiques',
                  },
                  {
                    id: 'confirmation',
                    label: 'Confirmation',
                    url: '/offre/individuelle/creation/confirmation',
                  },
                ]}
              />
            </BasicLayout>
          </>
        }
      />
      <Route
        path="/remboursements"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <BasicLayout mainHeading="Remboursements">
              <ReimbursementsTabs selectedOfferer={null} />
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
          offererNames: [{ id: 456, name: 'Offerer', allowedOnAdage: false }],
        },
        user: {
          currentUser: { id: 123 },
        },
      },
    }
  )
}

describe('useFocus', () => {
  it('should focus on back to nav link when user navigates to another page', async () => {
    renderUseFocusRoutes('/connection')
    expect(
      screen.getByRole('heading', { name: 'Connexion' })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: 'Log In' }))

    expect(screen.getByRole('heading', { name: 'Accueil' })).toBeInTheDocument()
    expect(document.activeElement?.id).toEqual('back-to-nav-link')
    await userEvent.tab()
    expect(document.activeElement?.id).not.toEqual('back-to-nav-link')
  })

  it('should focus on stepper active link when user navigates to another page with stepper', async () => {
    renderUseFocusRoutes('/offre/individuelle/creation')

    expect(
      screen.getByRole('heading', { name: 'Créer une offre individuelle' })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: '1 Détails' }))

    expect(
      screen.getByRole('heading', { name: 'Créer une offre individuelle' })
    ).toBeInTheDocument()
    expect(document.activeElement?.closest('li')?.id).toEqual('active')
    await userEvent.tab()
    expect(document.activeElement?.closest('li')?.id).not.toEqual('active')
  })

  it('should focus on tab active link when user navigates to another page with tabs', async () => {
    renderUseFocusRoutes('/remboursements')

    expect(
      screen.getByRole('heading', { name: 'Remboursements' })
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: /Justificatifs/ }))

    expect(
      screen.getByRole('heading', { name: 'Remboursements' })
    ).toBeInTheDocument()
    expect(document.activeElement?.closest('li')?.id).toEqual('selected')
    await userEvent.tab()
    expect(document.activeElement?.closest('li')?.id).not.toEqual('selected')
  })

  it('should focus on top of the page as a fallback', async () => {
    renderUseFocusRoutes('/accueil')

    expect(screen.getByRole('heading', { name: 'Accueil' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: 'Log Out' }))

    expect(
      screen.getByRole('heading', { name: 'Connexion' })
    ).toBeInTheDocument()
    expect(document.activeElement?.id).toEqual('go-to-content')
    await userEvent.tab()
    expect(document.activeElement?.id).not.toEqual('go-to-content')
  })
})
