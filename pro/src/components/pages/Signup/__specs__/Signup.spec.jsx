import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import Signup from '../Signup'

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
    listFeatures: jest.fn(),
  },
}))

describe('src | components | pages | Signup', () => {
  let store
  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: null,
      },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    })
    api.listFeatures.mockResolvedValue([])
  })
  afterEach(jest.resetAllMocks)

  it('should render logo and sign-up form', () => {
    // given
    const props = {
      location: {
        pathname: '/inscription',
      },
    }

    // when
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    expect(
      screen.getByRole('heading', { name: /Créer votre compte professionnel/ })
    ).toBeInTheDocument()
  })

  it('should render logo and confirmation page', () => {
    // given
    const props = {
      location: {
        pathname: '/inscription/confirmation',
      },
    }

    // when
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    expect(
      screen.getByText(/Votre compte est en cours de création./)
    ).toBeInTheDocument()
  })

  it('should render maintenance page when signup is unavailable', async () => {
    // given
    const props = {
      location: {
        pathname: '/inscription',
      },
    }
    const store = configureTestStore({
      features: {
        list: [{ isActive: false, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    })

    // when
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    expect(
      screen.getByRole('heading', { name: /Inscription indisponible/ })
    ).toBeInTheDocument()
  })

  it('should call media campaign tracker on mount only', async () => {
    // given
    api.listFeatures.mockResolvedValue([
      {
        isActive: true,
        nameKey: 'ENABLE_PRO_ACCOUNT_CREATION',
      },
    ])
    const props = {
      location: {},
    }

    // when
    const { rerender } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )
    // when rerender
    rerender(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    expect(campaignTracker.signUp).toHaveBeenCalledTimes(1)
  })
})
