import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { render } from '@testing-library/react'
import React from 'react'

import { firebaseConfig } from 'config/firebase'

import { useConfigureAnalytics } from '../useAnalytics'

const mockSetLogEvent = jest.fn()

jest.mock('@firebase/analytics', () => ({
  getAnalytics: jest.fn().mockReturnValue('getAnalyticsReturn'),
  initializeAnalytics: jest.fn(),
  setUserId: jest.fn(),
}))

jest.mock('@firebase/app', () => ({
  initializeApp: jest.fn().mockReturnValue({ setup: true }),
}))

const FakeApp = (): JSX.Element => {
  useConfigureAnalytics('userId')
  return <h1>Fake App</h1>
}

const renderFakeApp = async () => {
  return render(<FakeApp />)
}

test('should set logEvent and userId', async () => {
  jest.spyOn(React, 'useContext').mockImplementation(() => ({
    logEvent: jest.fn(),
    setLogEvent: mockSetLogEvent,
  }))

  await renderFakeApp()

  expect(initializeAnalytics).toHaveBeenNthCalledWith(
    1,
    { setup: true },
    { config: { send_page_view: false } }
  )
  expect(getAnalytics).toHaveBeenNthCalledWith(1, { setup: true })
  expect(firebase.initializeApp).toHaveBeenNthCalledWith(1, firebaseConfig)

  expect(setUserId).toHaveBeenNthCalledWith(1, 'getAnalyticsReturn', 'userId')

  expect(mockSetLogEvent).toHaveBeenNthCalledWith(1, expect.any(Function))
})
