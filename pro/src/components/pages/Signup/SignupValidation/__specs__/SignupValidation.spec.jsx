import '@testing-library/jest-dom'
import { render, waitFor } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import * as routerHelpers from 'components/router/helpers'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignupValidation from '../SignupValidation'

jest.mock('repository/pcapi/pcapi')

describe('src | components | pages | Signup | validation', () => {
  let history
  let props
  let store

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
    props = {
      history,
      location: {
        pathname: '/validation/AAA',
      },
      match: {
        params: {
          token: 'AAA',
        },
      },
      notifyError: () => {},
      notifySuccess: () => {},
    }
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
          <SignupValidation {...props} />
        </Router>
      </Provider>
    )
    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenCalledTimes(1)
    expect(validateUser).toHaveBeenNthCalledWith(1, props.match.params.token)
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
          <SignupValidation {...props} />
        </Router>
      </Provider>
    )
    // then the media campaign tracker should be called once
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)
  })

  it('should display a success message when token verification is successful', async () => {
    jest.spyOn(pcapi, 'validateUser').mockResolvedValue(true)
    const notifySuccess = jest.fn()
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation {...props} notifySuccess={notifySuccess} />
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
    jest.spyOn(pcapi, 'validateUser').mockRejectedValue({
      errors: {
        global: ['error1', 'error2'],
      },
    })
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignupValidation {...props} notifyError={notifyError} />
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
