import { setUser } from '@sentry/browser'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { URL_FOR_MAINTENANCE } from 'utils/config'

import { App } from '../App'

jest.mock('repository/pcapi/pcapi', () => ({
  getUserInformations: jest.fn(),
}))

const renderApp = ({ props, store }) => {
  return render(
    <Provider store={store}>
      <App {...props}>
        <p>Sub component</p>
      </App>
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

const mockSetAnalyticsUserId = jest.fn()
jest.mock('components/hooks/useAnalytics', () => {
  return jest.fn().mockReturnValue({
    setAnalyticsUserId: props => mockSetAnalyticsUserId(props),
  })
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
      data: { users: [{ ...user }] },
      user: { initialized: true },
    })
    props = {
      getCurrentUser,
      isFeaturesInitialized: false,
      isMaintenanceActivated: false,
      loadFeatures,
    }
    pcapi.getUserInformations.mockResolvedValue(user)
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

  it('should initialize firebase only once', () => {
    // When
    const { rerender } = renderApp({ props, store })
    rerender(renderApp)
    // Then
    expect(mockSetAnalyticsUserId).toHaveBeenCalledTimes(1)
  })
})
