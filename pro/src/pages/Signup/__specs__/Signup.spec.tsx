import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { api } from 'apiClient/api'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import { getOffererNameFactory } from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { Signup } from '../Signup'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getSirenInfo: vi.fn(),
  },
}))

const renderSignup = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <Routes>
      <Route path="/accueil" element="Connecté" />
      <Route path="/inscription" element={<Signup />}>
        {routesSignup.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
    </Routes>,
    options
  )

describe('src | components | pages | Signup', () => {
  it('should render logo and sign-up form', () => {
    renderSignup({
      initialRouterEntries: ['/inscription/compte/creation'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
    })

    expect(
      screen.getByRole('heading', { name: /Créez votre compte/ })
    ).toBeInTheDocument()

    expect(screen.getByLabelText(/Nom/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prénom/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Adresse email/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Mot de passe/)).toBeInTheDocument()
    expect(screen.getByText(/Téléphone/)).toBeInTheDocument()
    expect(
      screen.getByLabelText(
        'J’accepte d’être contacté par email pour recevoir les nouveautés du pass Culture et contribuer à son amélioration (facultatif)'
      )
    ).toBeInTheDocument()

    expect(screen.queryByText(/SIREN/)).not.toBeInTheDocument()

    expect(
      screen.getByText(/Conditions Générales d’Utilisation/)
    ).toHaveAttribute('href', 'https://pass.culture.fr/cgu-professionnels/')

    expect(
      screen.getAllByText('Charte des Données Personnelles')[0]
    ).toHaveAttribute('href', 'https://pass.culture.fr/donnees-personnelles/')

    expect(screen.getByText(/Contacter notre support/)).toHaveAttribute(
      'href',
      'mailto:support-pro@passculture.app'
    )
  })

  it('should render logo and confirmation page', () => {
    renderSignup({
      initialRouterEntries: ['/inscription/compte/confirmation'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
    })

    expect(
      screen.getByText(/Votre compte est en cours de création./)
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Vous allez recevoir un lien de confirmation par email. Cliquez sur ce lien pour confirmer la création de votre compte.'
      )
    ).toBeInTheDocument()
  })

  it('should redirect logged users on confirmation page', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Mon super cinéma',
        }),
        getOffererNameFactory({
          id: 1,
          name: 'Ma super librairie',
        }),
      ],
    })

    const user = sharedCurrentUserFactory()
    renderSignup({
      initialRouterEntries: ['/inscription/compte/confirmation'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
      user,
      storeOverrides: {
        user: {
          currentUser: user,
        },
        offerer: currentOffererFactory(),
      },
    })

    await waitFor(() => {
      expect(
        screen.queryByText(/Votre compte est en cours de création./)
      ).not.toBeInTheDocument()
    })

    expect(screen.getByText(/Connecté/)).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', () => {
    renderSignup({ initialRouterEntries: ['/inscription/compte/creation'] })

    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })
})
