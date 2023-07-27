import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignupJourneyRoutes from '../SignupJourneyRoutes'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
  },
}))

const renderSignupJourneyRoutes = () => {
  renderWithProviders(
    <Routes>
      <Route path="/parcours-inscription/*" element={<SignupJourneyRoutes />} />
      <Route path="/logout" element={<div>Logout</div>} />
    </Routes>,
    {
      storeOverrides: {
        user: {
          initialized: true,
          currentUser: {
            isAdmin: false,
            email: 'email@example.com',
            hasSeenProTutorials: true,
          },
        },
      },
      initialRouterEntries: ['/parcours-inscription/structure'],
    }
  )
}
const mockLogEvent = vi.fn()

describe('SignupJourneyRoutes::trackers', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  it('should render log logout event', async () => {
    renderSignupJourneyRoutes()
    await userEvent.click(screen.getByText('Se déconnecter'))
    await waitFor(() => {
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
      from: '/parcours-inscription/structure',
    })
  })
})
