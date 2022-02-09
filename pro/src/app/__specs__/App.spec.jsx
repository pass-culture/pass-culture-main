/*
 * @debt rtl "Gaël: bad use of act in testing library"
 */

import { setUser } from '@sentry/browser'
import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import { URL_FOR_MAINTENANCE } from 'utils/config'

import { App } from '../App'

const renderApp = async props => {
  await act(async () => {
    await render(
      <App {...props}>
        <p>Sub component</p>
      </App>
    )
  })
}

const getCurrentUser = ({ handleSuccess }) => {
  handleSuccess()
}

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

  beforeEach(() => {
    props = {
      featuresInitialized: false,
      getCurrentUser,
      isFeaturesInitialized: false,
      isMaintenanceActivated: false,
      loadFeatures,
    }
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    // When
    await renderApp(props)

    // Then
    expect(screen.getByText('Sub component')).toBeInTheDocument()
  })

  it('should render a Redirect component when isMaintenanceActivated is true', async () => {
    // When
    await renderApp({ ...props, isMaintenanceActivated: true })

    expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })

  it('should call Sentry setUser if current user is given', async () => {
    // When
    await renderApp({
      ...props,
      currentUser: { pk: 'pk_key' },
      isMaintenanceActivated: true,
    })

    // Then
    expect(setUser).toHaveBeenCalledWith({ id: 'pk_key' })
  })

  it('should load features', async () => {
    // When
    await renderApp(props)

    // Then
    expect(loadFeatures).toHaveBeenCalledWith()
  })
})
