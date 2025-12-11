import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { routesSignupJourney } from '@/app/AppRouter/subroutesSignupJourneyMap'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignupJourneyRoutes } from '../SignupJourneyRoutes'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
    signout: vi.fn(),
  },
}))

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
    // because we directly use fetch in logout
    fetchMock.mockResponse((req) => {
      if (req.url.includes('/users/signout') && req.method === 'GET') {
        return { status: 200, body: JSON.stringify({ success: true }) }
      }
      return { status: 404 }
    })
    const windowLocationReloadSpy = vi.fn()
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      reload: windowLocationReloadSpy,
    })
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderSignupJourneyRoutes()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText('Se déconnecter'))

    expect(windowLocationReloadSpy).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
      from: '/inscription/structure/recherche',
    })
  })
})
