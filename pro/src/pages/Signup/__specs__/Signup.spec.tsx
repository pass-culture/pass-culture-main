import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import { renderWithProviders } from 'utils/renderWithProviders'

import Signup from '../Signup'

jest.mock('tracking/mediaCampaignsTracking')

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
    listFeatures: jest.fn(),
    listOfferersNames: jest.fn(),
    getSirenInfo: jest.fn(),
  },
}))

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
  afterEach(jest.resetAllMocks)

  it('should render logo and sign-up form', async () => {
    // when
    renderWithProviders(<Signup />, {
      storeOverrides,
      initialRouterEntries: ['/'], // /inscription
    })
    await waitFor(() => expect(campaignTracker.signUp).toHaveBeenCalled())

    // then
    expect(
      screen.getByRole('heading', { name: /Créer votre compte/ })
    ).toBeInTheDocument()
  })

  it('should render logo and confirmation page', async () => {
    // when
    renderWithProviders(<Signup />, {
      storeOverrides,
      initialRouterEntries: ['/confirmation'], // /inscription/confirmation
    })
    await waitFor(() => expect(campaignTracker.signUp).toHaveBeenCalled())

    // then
    expect(
      screen.getByText(/Votre compte est en cours de création./)
    ).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', async () => {
    // given
    const storeOverrides = {
      features: {
        list: [{ isActive: false, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }

    // when
    renderWithProviders(<Signup />, {
      storeOverrides,
      initialRouterEntries: ['/inscription'],
    })
    await waitFor(() => expect(campaignTracker.signUp).toHaveBeenCalled())

    // then
    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })

  it('should call media campaign tracker on mount only', async () => {
    // given
    const storeOverrides = {
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }

    // when
    const { rerender } = renderWithProviders(<Signup />, {
      storeOverrides,
      initialRouterEntries: ['/inscription'],
    })

    // when rerender
    rerender(<Signup />)

    // then
    expect(campaignTracker.signUp).toHaveBeenCalledTimes(1)
  })
})
