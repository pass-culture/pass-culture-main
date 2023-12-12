import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

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
      <Route path="/parcours-inscription/*" element={<SignupJourneyRoutes />} />
      <Route path="/connexion" element={<div>Connexion</div>} />
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
    }))
  })

  it('should logout', async () => {
    renderSignupJourneyRoutes()

    vi.spyOn(api, 'signout').mockResolvedValue()
    await userEvent.click(screen.getByText('Se déconnecter'))
    await waitFor(() => {
      expect(api.signout).toHaveBeenCalledTimes(1)
    })
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
      from: '/parcours-inscription/structure',
    })
  })
})
