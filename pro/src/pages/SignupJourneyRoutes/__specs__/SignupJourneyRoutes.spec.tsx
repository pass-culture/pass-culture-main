import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SignupJourneyRoutes } from '../SignupJourneyRoutes'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
  },
}))

const renderSignupJourneyRoutes = () => {
  renderWithProviders(
    <Routes>
      <Route path="/parcours-inscription" element={<SignupJourneyRoutes />}>
        {routesSignupJourney.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/structure'],
    }
  )
}

describe('SignupJourneyRoutes', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render component', async () => {
    renderSignupJourneyRoutes()
    await waitFor(() => {
      expect(
        screen.getByText('Renseignez le SIRET de votre structure')
      ).toBeInTheDocument()
    })
  })
})
