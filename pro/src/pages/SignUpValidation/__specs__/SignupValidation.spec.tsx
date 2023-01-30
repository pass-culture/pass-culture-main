import { render, waitFor } from '@testing-library/react'
import type { Action, History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import reactRouter from 'react-router'
import { Router } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import type { IUseCurrentUserReturn } from 'hooks/useCurrentUser'
import * as useCurrentUser from 'hooks/useCurrentUser'
import * as useNotification from 'hooks/useNotification'
import { configureTestStore } from 'store/testUtils'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignUpValidation from '../SignUpValidation'

jest.mock('repository/pcapi/pcapi')
jest.mock('hooks/useCurrentUser')
jest.mock('hooks/useNotification')

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
      user: {
        currentUser: null,
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
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {},
    } as IUseCurrentUserReturn)
  })

  afterEach(jest.resetAllMocks)

  it('should redirect to home page if the user is logged in', async () => {
    const validateUser = jest.spyOn(api, 'validateUser')
    const redirect = jest.fn()
    jest.spyOn(reactRouter, 'useHistory').mockImplementation(() => ({
      push: redirect,
      length: 0,
      action: 'REPLACE' as Action,
      location: {
        pathname: '',
        search: '',
        state: '',
        hash: '',
      },
      replace: jest.fn(),
      go: jest.fn(),
      goBack: jest.fn(),
      goForward: jest.fn(),
      block: jest.fn(),
      listen: jest.fn(),
      createHref: jest.fn(),
    }))
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {
        id: '123',
      },
    } as IUseCurrentUserReturn)
    // when the user is logged in and lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page
    expect(redirect).toHaveBeenCalledTimes(1)
    expect(redirect).toHaveBeenNthCalledWith(1, '/')
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = jest.spyOn(api, 'validateUser').mockResolvedValue()
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
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
    jest.spyOn(api, 'validateUser').mockResolvedValue()
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // then the media campaign tracker should be called once
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)
  })

  it('should display a success message when token verification is successful', async () => {
    jest.spyOn(api, 'validateUser').mockResolvedValue()
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      success: notifySuccess,
    }))
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
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
    jest.spyOn(api, 'validateUser').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['error1', 'error2'],
          },
        } as ApiResult,
        ''
      )
    )
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
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
