import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import * as useAnalytics from 'app/App/analytics/firebase'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { SignupJourneyRoutes } from '../SignupJourneyRoutes'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
    signout: vi.fn(),
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
      <Route path="/connexion" element={<div>Connexion</div>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/structure'],
    }
  )
}
const mockLogEvent = vi.fn()

describe('SignupJourneyRoutes::trackers', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track logout', async () => {
    renderSignupJourneyRoutes()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText('Se déconnecter'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
      from: '/parcours-inscription/structure',
    })
  })
})
