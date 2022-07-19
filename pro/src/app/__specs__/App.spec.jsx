import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { App } from '../App'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import { URL_FOR_MAINTENANCE } from 'utils/config'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import { setUser } from '@sentry/browser'

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

  it('should render App and children components when isMaintenanceActivated is false', () => {
    // When
    renderApp({ props, store })

    // Then
    expect(screen.getByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({ id: user.id })
  })

  it('should render a Redirect component when isMaintenanceActivated is true', () => {
    // When
    props = {
      ...props,
      isMaintenanceActivated: true,
    }
    renderApp({ props, store })

    expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })

  it('should load features', async () => {
    // When
    renderApp({ props, store })

    // Then
    expect(loadFeatures).toHaveBeenCalledWith()
  })
})
