import * as firebaseAnalytics from '@firebase/analytics'
import * as firebase from '@firebase/app'
import * as firebaseRemoteConfig from '@firebase/remote-config'
import { waitFor } from '@testing-library/react'
import React from 'react'
import { expect, vi } from 'vitest'

import { firebaseConfig } from 'config/firebase'
import { renderWithProviders } from 'utils/renderWithProviders'

import { useConfigureFirebase } from '../useAnalytics'

vi.mock('@firebase/analytics', () => ({
  getAnalytics: vi.fn(),
  initializeAnalytics: vi.fn(),
  setUserId: vi.fn(),
  isSupported: vi.fn(),
  logEvent: vi.fn(),
}))

vi.mock('@firebase/app', () => ({
  initializeApp: vi.fn(),
}))

vi.mock('@firebase/remote-config', () => ({
  fetchAndActivate: vi.fn(),
  getRemoteConfig: vi.fn(),
  getAll: vi.fn(),
}))

const FakeApp = ({
  isCookieEnabled,
}: {
  isCookieEnabled: boolean
}): JSX.Element => {
  useConfigureFirebase({ currentUserId: 'userId', isCookieEnabled })

  return <h1>Fake App</h1>
}

const renderFakeApp = async ({
  isCookieEnabled,
}: {
  isCookieEnabled: boolean
}) => {
  return renderWithProviders(<FakeApp isCookieEnabled={isCookieEnabled} />)
}

describe('useAnalytics', () => {
  it('should set logEvent and userId if cookie is set', async () => {
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValue(true)
    vi.spyOn(firebase, 'initializeApp').mockReturnValue({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })
    vi.spyOn(firebaseAnalytics, 'setUserId')
    vi.spyOn(firebaseAnalytics, 'initializeAnalytics')
    vi.spyOn(firebaseAnalytics, 'getAnalytics').mockReturnValueOnce(
      'getAnalyticsReturn'
    )

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockResolvedValue(true)
    vi.spyOn(firebaseRemoteConfig, 'getAll').mockResolvedValue({
      A: { asString: () => 'true' },
    })

    await renderFakeApp({ isCookieEnabled: true })

    await waitFor(() => {
      expect(firebaseAnalytics.isSupported).toHaveBeenCalledTimes(1)
    })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).toHaveBeenCalledTimes(1)
    })

    expect(firebaseAnalytics.initializeAnalytics).toHaveBeenNthCalledWith(
      1,
      {
        name: '',
        options: {},
        automaticDataCollectionEnabled: true,
      },
      { config: { send_page_view: false } }
    )
    expect(firebaseAnalytics.getAnalytics).toHaveBeenCalledTimes(1)
    expect(firebaseAnalytics.getAnalytics).toHaveBeenNthCalledWith(1, {
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })
    expect(firebase.initializeApp).toHaveBeenCalledTimes(1)
    expect(firebase.initializeApp).toHaveBeenNthCalledWith(1, firebaseConfig)
    expect(firebaseAnalytics.setUserId).toHaveBeenCalledTimes(1)
    expect(firebaseAnalytics.setUserId).toHaveBeenNthCalledWith(
      1,
      'getAnalyticsReturn',
      'userId'
    )
  })

  it('should not load if cookie is disabled', async () => {
    await renderFakeApp({ isCookieEnabled: false })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).not.toHaveBeenCalled()

      expect(firebaseAnalytics.getAnalytics).not.toHaveBeenCalled()
      expect(firebase.initializeApp).not.toHaveBeenCalled()
      expect(firebaseAnalytics.setUserId).not.toHaveBeenCalled()
    })
  })
})
