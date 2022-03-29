import '@testing-library/jest-dom'
import { render, waitFor } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import type { History } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import reactRouter from 'react-router'
import { Router } from 'react-router-dom'

import * as routerHelpers from 'components/router/helpers'
import * as useNotification from 'components/hooks/useNotification'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignupValidation from '../SignupValidation'

jest.mock('repository/pcapi/pcapi')
jest.mock('components/hooks/useNotification')

describe('src | components | pages | Signup | validation', () => {
  let history: History
  let store = configureTestStore()
  const mockUseNotification = {
    close: jest.fn(),
    error: jest.fn(),
    pending: jest.fn(),
    information: jest.fn(),
    success: jest.fn(),
  }

  beforeEach(() => {
    store = configureTestStore({
      data: {
        users: null,
      },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    })
    history = createBrowserHistory()
    jest.spyOn(reactRouter, 'useParams').mockReturnValue({ token: 'AAA' })
    store = configureTestStore()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
    }))
  })

  afterEach(jest.resetAllMocks)

  it('should redirect to home page if the user is logged in', async () => {
    const validateUser = jest.spyOn(pcapi, 'validateUser')
    const redirect = jest
      .spyOn(routerHelpers, 'redirectLoggedUser')
      .mockImplementation(() => {})
    // when the user is logged in and lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation {...props} currentUser={{ id: 'CMOI' }} />
        </Router>
      </Provider>
    )
    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page

    expect(redirect).toHaveBeenCalledTimes(1)
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = jest
      .spyOn(pcapi, 'validateUser')
      .mockResolvedValue(true)
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation />
        </Router>
      </Provider>
    )
    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenCalledTimes(1)
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')
    // and he should be redirected to signin page
    await waitFor(() => {
      expect(history.location.pathname).toBe('/connexion')
    })
  })

  it('should call media campaign tracker once', () => {
    jest.spyOn(pcapi, 'validateUser').mockResolvedValue(true)
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation />
        </Router>
      </Provider>
    )
    // then the media campaign tracker should be called once
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)
  })

  it('should display a success message when token verification is successful', async () => {
    jest.spyOn(pcapi, 'validateUser').mockResolvedValue(true)
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      success: notifySuccess,
    }))
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation />
        </Router>
      </Provider>
    )
    // when his token is successfully validated
    // then a success message should be dispatched
    await waitFor(() => {
      expect(notifySuccess).toHaveBeenNthCalledWith(
        1,
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
    })
  })

  it('should display an error message when token verification is not successful', async () => {
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      error: notifyError,
    }))
    jest.spyOn(pcapi, 'validateUser').mockRejectedValue({
      errors: {
        global: ['error1', 'error2'],
      },
    })
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation />
        </Router>
      </Provider>
    )
    // when his token is not successfully validated
    // then an error message should be dispatched
    await waitFor(() => {
      expect(notifyError).toHaveBeenNthCalledWith(1, ['error1', 'error2'])
    })
  })
})
