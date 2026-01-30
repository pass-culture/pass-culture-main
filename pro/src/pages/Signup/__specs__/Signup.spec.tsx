import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { routesSignup } from '@/app/AppRouter/subroutesSignupMap'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Signup } from '../Signup'

vi.mock('@/apiClient/api', () => ({
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
    expect(
      screen.getByLabelText(
        'J’accepte d’être contacté par email pour recevoir les nouveautés du pass Culture et contribuer à son amélioration (facultatif)'
      )
    ).toBeInTheDocument()

    expect(screen.queryByText(/SIREN/)).not.toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /Conditions générales d’utilisation/ })
    ).toHaveAttribute('href', 'https://pass.culture.fr/cgu-professionnels/')

    expect(
      screen.getByRole('link', { name: 'Charte des Données Personnelles' })
    ).toHaveAttribute('href', 'https://pass.culture.fr/donnees-personnelles/')
  })

  it('should render logo and confirmation page', () => {
    renderSignup({
      initialRouterEntries: ['/inscription/compte/confirmation'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
    })

    expect(screen.getByText(/Validez votre adresse email/)).toBeInTheDocument()

    expect(
      screen.getByText('Cliquez sur le lien envoyé par email')
    ).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', () => {
    renderSignup({ initialRouterEntries: ['/inscription/compte/creation'] })

    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })
})
