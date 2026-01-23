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

const renderUseFocusRoutes = (url = '/accueil', isConnected = true) => {
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
      <Route
        path="/simple-page"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <SignUpLayout mainHeading="Simple Page">
              <div>Content without stepper or tabs</div>
            </SignUpLayout>
          </>
        }
      />
      <Route
        path="/not-connected-page"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <SignUpLayout mainHeading="Not Connected Page">
              <div>Content for not connected user</div>
            </SignUpLayout>
          </>
        }
      />
      <Route
        path="/no-go-to-content"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <div>
              <h1>Page Without Go To Content</h1>
            </div>
          </>
        }
      />
      <Route
        path="/offre/stepper-no-active"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <BasicLayout mainHeading="Créer une offre individuelle">
              <div id="stepper">
                <ul>
                  <li>Step 1</li>
                  <li>Step 2</li>
                </ul>
              </div>
            </BasicLayout>
          </>
        }
      />
      <Route
        path="/remboursements-no-active"
        element={
          <>
            <FocusTopPageOrBackToNavLink />
            <BasicLayout mainHeading="Remboursements">
              <div id="tablist">
                <ul>
                  <li>Tab 1</li>
                  <li>Tab 2</li>
                </ul>
              </div>
            </BasicLayout>
          </>
        }
      />
    </Routes>,
    {
      initialRouterEntries: [url],
      storeOverrides: {
        offerer: {
          offererNames: [{ id: 456, name: 'Offerer' }],
        },
        user: {
          currentUser: isConnected ? { id: 123 } : null,
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

  it('should focus on go-to-content link when connected and no back-to-nav, stepper or tabs', () => {
    renderUseFocusRoutes('/simple-page')

    expect(
      screen.getByRole('heading', { name: 'Simple Page' })
    ).toBeInTheDocument()
    expect(document.activeElement?.id).toEqual('go-to-content')
  })

  it('should focus on go-to-content when not connected and go-to-content element exists', () => {
    renderUseFocusRoutes('/not-connected-page', false)

    expect(
      screen.getByRole('heading', { name: 'Not Connected Page' })
    ).toBeInTheDocument()
    expect(document.activeElement?.id).toEqual('go-to-content')
  })

  it('should focus on body when not connected and no go-to-content element', () => {
    renderUseFocusRoutes('/no-go-to-content', false)

    expect(screen.getByText('Page Without Go To Content')).toBeInTheDocument()
    // Focus should remain on body as fallback
    expect(document.activeElement?.tagName).toEqual('BODY')
  })

  it('should not focus on stepper when stepper exists but no active step', () => {
    renderUseFocusRoutes('/offre/stepper-no-active')

    expect(
      screen.getByRole('heading', { name: 'Créer une offre individuelle' })
    ).toBeInTheDocument()
    // Focus should remain on body when stepper exists but no active step
    expect(document.activeElement?.tagName).toEqual('BODY')
  })

  it('should not focus on tabs when tabs exist but no active tab', () => {
    renderUseFocusRoutes('/remboursements-no-active')

    expect(
      screen.getByRole('heading', { name: 'Remboursements' })
    ).toBeInTheDocument()
    // Focus should remain on body when tabs exist but no active tab
    expect(document.activeElement?.tagName).toEqual('BODY')
  })

  it('should not apply focus logic on excluded routes like /hub', () => {
    // /hub is an actual route in routesMap with RouteId.Hub which is excluded
    renderWithProviders(
      <Routes>
        <Route
          path="/hub"
          element={
            <>
              <FocusTopPageOrBackToNavLink />
              <BasicLayout mainHeading="Changer de structure">
                <div>Hub content</div>
              </BasicLayout>
            </>
          }
        />
      </Routes>,
      {
        initialRouterEntries: ['/hub'],
        storeOverrides: {
          user: {
            currentUser: { id: 123 },
          },
        },
      }
    )

    expect(
      screen.getByRole('heading', { name: 'Changer de structure' })
    ).toBeInTheDocument()
    // Focus should remain on body since the route is excluded from focus logic
    expect(document.activeElement?.tagName).toEqual('BODY')
  })
})
