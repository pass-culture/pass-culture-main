import * as firebaseAnalytics from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { render, waitFor } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { firebaseConfig } from 'config/firebase'

import { useConfigureFirebase } from '../useAnalytics'

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

jest.mock('@firebase/remote-config', () => ({
  fetchAndActivate: jest.fn().mockResolvedValue({}),
  getRemoteConfig: jest.fn(),
  getAll: () => {
    return { A: { asString: () => 'true' } }
  },
}))

const FakeApp = (): JSX.Element => {
  useConfigureFirebase('userId')
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
