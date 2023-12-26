import { screen } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

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
      initialRouterEntries: ['/inscription'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
    })

    expect(
      screen.getByRole('heading', { name: /Créer votre compte/ })
    ).toBeInTheDocument()
  })

  it('should render logo and confirmation page', () => {
    renderSignup({
      initialRouterEntries: ['/inscription/confirmation'],
      features: ['ENABLE_PRO_ACCOUNT_CREATION'],
    })

    expect(
      screen.getByText(/Votre compte est en cours de création./)
    ).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', () => {
    renderSignup({ initialRouterEntries: ['/inscription'] })

    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })
})
