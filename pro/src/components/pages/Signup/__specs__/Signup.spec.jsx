import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import configureStore from 'store'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import Signup from '../Signup'

jest.mock('repository/pcapi/pcapi', () => ({
  loadFeatures: jest.fn(),
}))

describe('src | components | pages | Signup', () => {
  let store
  beforeEach(() => {
    store = configureStore({
      data: {
        users: null,
      },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }).store
    pcapi.loadFeatures.mockResolvedValue([])
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
    const store = configureStore({
      features: {
        list: [{ isActive: false, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    }).store

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
    pcapi.loadFeatures.mockResolvedValue([
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
