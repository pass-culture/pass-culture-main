import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

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
  storeOverrides: Partial<RootState> = {}
) => {
  renderWithProviders(
    <Routes>
      <Route path="/parcours-inscription/*" element={<SignupJourneyRoutes />} />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/structure'],
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
      expect(
        screen.getByText('Renseignez le SIRET de votre structure')
      ).toBeInTheDocument()
    })
  })
})
