import * as firebaseAnalytics from '@firebase/analytics'
import * as firebase from '@firebase/app'
import * as firebaseRemoteConfig from '@firebase/remote-config'
import { waitFor } from '@testing-library/react'
import { firebaseConfig } from 'commons/config/firebase'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { expect, vi } from 'vitest'

import { destroyFirebase, useFirebase } from '../firebase'

vi.mock('@firebase/analytics', () => ({
  getAnalytics: vi.fn(),
  initializeAnalytics: vi.fn(),
  setUserId: vi.fn(),
  isSupported: vi.fn(),
  logEvent: vi.fn(),
}))

vi.mock('@firebase/app', () => ({
  initializeApp: vi.fn(),
  deleteApp: vi.fn(),
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
  useFirebase(isCookieEnabled)

  return <h1>Fake App {isCookieEnabled ? 'yes' : 'no'}</h1>
}

const user = sharedCurrentUserFactory()
const renderFakeApp = ({ isCookieEnabled }: { isCookieEnabled: boolean }) => {
  renderWithProviders(<FakeApp isCookieEnabled={isCookieEnabled} />, {
    user,
  })
}

describe('useFirebase', () => {
  beforeEach(async () => {
    vi.spyOn(firebase, 'deleteApp').mockResolvedValue()
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValue(true)
    await destroyFirebase()
  })

  it('should set logEvent and userId if cookie is set', async () => {
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValue(true)
    vi.spyOn(firebase, 'initializeApp').mockReturnValue({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })
    vi.spyOn(firebaseAnalytics, 'setUserId')
    vi.spyOn(firebaseAnalytics, 'initializeAnalytics')
    vi.spyOn(firebaseAnalytics, 'getAnalytics').mockReturnValue(
      'getAnalyticsReturn' as unknown as firebaseAnalytics.Analytics
    )

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockResolvedValue(true)
    vi.spyOn(firebaseRemoteConfig, 'getAll').mockResolvedValue({
      A: {
        asString: () => 'true',
        asBoolean: vi.fn(),
        asNumber: vi.fn(),
        getSource: vi.fn(),
      },
    })

    renderFakeApp({ isCookieEnabled: true })

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
      user.id.toString()
    )
  })

  it('should not load if cookie is disabled', async () => {
    renderFakeApp({ isCookieEnabled: false })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).not.toHaveBeenCalled()

      expect(firebaseAnalytics.getAnalytics).not.toHaveBeenCalled()
      expect(firebase.initializeApp).not.toHaveBeenCalled()
      expect(firebaseAnalytics.setUserId).not.toHaveBeenCalled()
    })
  })

  it('should destroy firebase when consent is taken back', async () => {
    vi.spyOn(firebase, 'initializeApp').mockReturnValue({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })

    renderFakeApp({ isCookieEnabled: true })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).toHaveBeenCalledTimes(1)
    })

    renderFakeApp({ isCookieEnabled: false })

    await waitFor(() => {
      expect(firebase.deleteApp).toHaveBeenCalled()
    })
  })
})
