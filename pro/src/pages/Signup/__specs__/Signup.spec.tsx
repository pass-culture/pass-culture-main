import { screen } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Signup } from '../Signup'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getSirenInfo: vi.fn(),
  },
}))

const renderSignup = (storeOverrides: any, initialUrl: string) =>
  renderWithProviders(
    <Routes>
      <Route path="/inscription" element={<Signup />}>
        {routesSignup.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: [initialUrl],
    }
  )

describe('src | components | pages | Signup', () => {
  let storeOverrides: any
  beforeEach(() => {
    storeOverrides = {
      user: {
        currentUser: null,
      },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }
  })

  it('should render logo and sign-up form', () => {
    renderSignup(storeOverrides, '/inscription')

    expect(
      screen.getByRole('heading', { name: /Créer votre compte/ })
    ).toBeInTheDocument()
  })

  it('should render logo and confirmation page', () => {
    renderSignup(storeOverrides, '/inscription/confirmation')

    expect(
      screen.getByText(/Votre compte est en cours de création./)
    ).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', () => {
    const storeOverrides = {
      features: {
        list: [{ isActive: false, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }

    renderSignup(storeOverrides, '/inscription')

    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })
})
