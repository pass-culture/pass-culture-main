import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { routesSignupJourney } from '@/app/AppRouter/subroutesSignupJourneyMap'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as logoutModule from '@/commons/store/user/dispatchers/logout'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignupJourneyRoutes } from '../SignupJourneyRoutes'

const renderSignupJourneyRoutes = () => {
  renderWithProviders(
    <Routes>
      <Route path="/inscription/structure" element={<SignupJourneyRoutes />}>
        {routesSignupJourney.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
      <Route path="/connexion" element={<div>Connexion</div>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche'],
    }
  )
}
const mockLogEvent = vi.fn()

describe('SignupJourneyRoutes::trackers', () => {
  it('should track logout', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    const logoutSpy = vi
      .spyOn(logoutModule, 'logout')
      .mockImplementation(vi.fn())

    renderSignupJourneyRoutes()

    await userEvent.click(screen.getByTestId('profile-button'))
    await userEvent.click(screen.getByText('Se déconnecter'))

    expect(logoutSpy).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
      from: '/inscription/structure/recherche',
    })
  })
})
