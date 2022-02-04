import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import Logo from 'components/layout/Logo'
import * as pcapi from 'repository/pcapi/pcapi'
import configureStore from 'store'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import { enzymeWaitFor } from 'utils/testHelpers'

import Signup from '../Signup'
import SignupConfirmation from '../SignupConfirmation/SignupConfirmation'
import SignupForm from '../SignupForm/SignupForm'
import SignupUnavailable from '../SignupUnavailable/SignupUnavailable'

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
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const logo = wrapper.find(Logo)
    const signupForm = wrapper.find(SignupForm)
    expect(logo).toHaveLength(1)
    expect(signupForm).toHaveLength(1)
  })

  it('should render logo and confirmation page', () => {
    // given
    const props = {
      location: {
        pathname: '/inscription/confirmation',
      },
    }

    // when
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const logo = wrapper.find(Logo)
    const signupConfirmation = wrapper.find(SignupConfirmation)
    expect(logo).toHaveLength(1)
    expect(signupConfirmation).toHaveLength(1)
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
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const unavailablePage = wrapper.find(SignupUnavailable)
    expect(unavailablePage).toHaveLength(1)
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
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Signup {...props} />
        </MemoryRouter>
      </Provider>
    )
    wrapper.update()

    // then
    await enzymeWaitFor(() =>
      expect(campaignTracker.signUp).toHaveBeenCalledTimes(1)
    )

    // when rerender
    wrapper.setProps(props)

    // then
    await enzymeWaitFor(() =>
      expect(campaignTracker.signUp).toHaveBeenCalledTimes(1)
    )
  })
})
