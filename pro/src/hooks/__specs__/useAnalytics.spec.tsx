import * as firebaseAnalytics from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { render, waitFor } from '@testing-library/react'
import React from 'react'
import { MemoryRouter, Route } from 'react-router'

import NavigationLogger from 'components/router/NavigationLogger'
import { firebaseConfig } from 'config/firebase'
import { AnalyticsContextProvider } from 'context/analyticsContext'
import { Events } from 'core/FirebaseEvents/constants'

import { useConfigureAnalytics } from '../useAnalytics'

const mockSetLogEvent = jest.fn()

jest.mock('@firebase/analytics', () => {
  return {
    getAnalytics: jest.fn().mockReturnValue('getAnalyticsReturn'),
    initializeAnalytics: jest.fn(),
    setUserId: jest.fn(),
    isSupported: jest.fn().mockResolvedValue(true),
    logEvent: jest.fn(),
  }
})

jest.mock('@firebase/app', () => ({
  initializeApp: jest.fn().mockReturnValue({ setup: true }),
}))

const FakeApp = (): JSX.Element => {
  useConfigureAnalytics('userId')
  return <h1>Fake App</h1>
}

const renderFakeApp = async () => {
  return render(
    <MemoryRouter>
      <FakeApp />
    </MemoryRouter>
  )
}

test('should set logEvent and userId', async () => {
  jest.spyOn(React, 'useContext').mockImplementation(() => ({
    logEvent: jest.fn(),
    setLogEvent: mockSetLogEvent,
  }))

  await renderFakeApp()

  await waitFor(() => {
    expect(firebaseAnalytics.initializeAnalytics).toHaveBeenCalledTimes(1)
    expect(firebaseAnalytics.initializeAnalytics).toHaveBeenNthCalledWith(
      1,
      { setup: true },
      { config: { send_page_view: false } }
    )
    expect(firebaseAnalytics.getAnalytics).toHaveBeenCalledTimes(1)
    expect(firebaseAnalytics.getAnalytics).toHaveBeenNthCalledWith(1, {
      setup: true,
    })
    expect(firebase.initializeApp).toHaveBeenCalledTimes(1)
    expect(firebase.initializeApp).toHaveBeenNthCalledWith(1, firebaseConfig)
    expect(firebaseAnalytics.setUserId).toHaveBeenCalledTimes(1)
    expect(firebaseAnalytics.setUserId).toHaveBeenNthCalledWith(
      1,
      'getAnalyticsReturn',
      'userId'
    )
    expect(mockSetLogEvent).toHaveBeenCalledTimes(1)
    expect(mockSetLogEvent).toHaveBeenNthCalledWith(1, expect.any(Function))
  })
})

const renderFakeAppWithTrackedLinks = () => {
  return render(
    <AnalyticsContextProvider>
      <MemoryRouter
        initialEntries={[
          '/structures?utm_campaign=push_offre_local&utm_medium=batch&utm_source=push',
        ]}
      >
        <NavigationLogger />
        <FakeAppWithTrackedLinks>
          <Route path="/structures">
            <h1>Fake Structure</h1>
          </Route>
        </FakeAppWithTrackedLinks>
      </MemoryRouter>
    </AnalyticsContextProvider>
  )
}

interface IFakeAppProps {
  children: JSX.Element
}
const FakeAppWithTrackedLinks = ({ children }: IFakeAppProps): JSX.Element => {
  useConfigureAnalytics('userId')
  return children
}

test('should trigger a logEvent', async () => {
  await renderFakeAppWithTrackedLinks()
  await waitFor(() => {
    expect(firebaseAnalytics.logEvent).toHaveBeenNthCalledWith(
      1,
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: '/structures',
        traffic_campaign: 'push_offre_local',
        traffic_medium: 'batch',
        traffic_source: 'push',
      }
    )
    expect(firebaseAnalytics.logEvent).toHaveBeenNthCalledWith(
      2,
      'getAnalyticsReturn',
      Events.UTM_TRACKING_CAMPAIGN,
      {
        traffic_campaign: 'push_offre_local',
        traffic_medium: 'batch',
        traffic_source: 'push',
      }
    )
  })
})
