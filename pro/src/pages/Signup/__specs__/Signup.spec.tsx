import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { routesSignup } from '@/app/AppRouter/subroutesSignupMap'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Signup } from '../Signup'

vi.mock('@/apiClient/api', () => ({
  api: {
    getSirenInfo: vi.fn(),
    getProfile: vi.fn(),
    listOfferersNames: vi.fn(),
    listFeatures: vi.fn(),
  },
}))

const renderSignup = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(null, {
    ...options,
    routes: [
      { path: '/accueil', element: 'Connecté' },
      {
        path: '/inscription',
        element: <Signup />,
        hydrateFallbackElement: <></>,
        children: routesSignup.map((route) => ({
          ...route,
          loader: undefined,
        })),
      },
    ],
  })

describe('src | components | pages | Signup', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSignup({
      initialRouterEntries: ['/inscription/compte/creation'],
    })

    await screen.findByRole('heading', { name: /Créez votre compte/ })
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render logo and sign-up form', async () => {
    renderSignup({ initialRouterEntries: ['/inscription/compte/creation'] })

    expect(
      await screen.findByRole('heading', { name: /Créez votre compte/ })
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
      screen.getByRole('link', { name: /Charte des Données Personnelles/ })
    ).toHaveAttribute('href', 'https://pass.culture.fr/donnees-personnelles/')
  })

  it('should render logo and confirmation page', async () => {
    renderSignup({ initialRouterEntries: ['/inscription/compte/confirmation'] })

    expect(
      await screen.findByText(/Validez votre adresse email/)
    ).toBeInTheDocument()

    expect(
      screen.getByText('Cliquez sur le lien envoyé par email')
    ).toBeInTheDocument()
  })
})
