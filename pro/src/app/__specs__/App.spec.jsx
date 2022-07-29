import '@testing-library/jest-dom'

import { setUser } from '@sentry/browser'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import { URL_FOR_MAINTENANCE } from 'utils/config'

import { App } from '../App'

jest.mock('apiClient/api', () => ({
  api: { getProfile: jest.fn() },
}))

const renderApp = ({ props, store }) => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <App {...props}>
          <p>Sub component</p>
        </App>
      </MemoryRouter>
    </Provider>
  )
}

const getCurrentUser = jest.fn()
const loadFeatures = jest.fn()

jest.mock('@sentry/browser', () => ({
  setUser: jest.fn(),
}))

jest.spyOn(window, 'scrollTo').mockImplementation()

delete window.location
window.location = {}
const setHrefSpy = jest.fn()
Object.defineProperty(window.location, 'href', {
  set: setHrefSpy,
})

describe('src | App', () => {
  let props
  let store
  let user

  beforeEach(() => {
    user = {
      id: 'user_id',
      publicName: 'François',
      isAdmin: false,
    }
    store = configureTestStore({
      user: { initialized: true, currentUser: user },
    })
    props = {
      getCurrentUser,
      isFeaturesInitialized: false,
      isMaintenanceActivated: false,
      loadFeatures,
    }
    jest.spyOn(api, 'getProfile').mockResolvedValue(user)
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    // When
    renderApp({ props, store })

    // Then
    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({ id: user.id })
  })

  it('should render a Redirect component when isMaintenanceActivated is true', async () => {
    // When
    props = {
      ...props,
      isMaintenanceActivated: true,
    }
    renderApp({ props, store })

    await waitFor(() => {
      expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
    })
  })

  it('should load features', async () => {
    // When
    renderApp({ props, store })

    // Then
    await screen.findByText('Sub component')
    expect(loadFeatures).toHaveBeenCalledWith()
  })
})
