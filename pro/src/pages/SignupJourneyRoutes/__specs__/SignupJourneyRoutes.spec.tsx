import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { api } from 'apiClient/api'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignupJourneyRoutes from '../SignupJourneyRoutes'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: jest.fn(),
  },
}))

const renderSignupJourneyRoutes = async (
  storeOverride?: Partial<RootState>
) => {
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/parcours-inscription/*"
          element={<SignupJourneyRoutes />}
        />
      </Routes>
    </>,
    {
      ...storeOverride,
      initialRouterEntries: ['/parcours-inscription/authentification'],
    }
  )
}

describe('SignupJourneyRoutes', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          publicName: 'John Do',
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    }

    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render component', async () => {
    renderSignupJourneyRoutes(store)
    await waitFor(() => {
      expect(screen.getByText('Activité')).toBeInTheDocument()
    })
  })
})
