import * as firebaseAnalytics from '@firebase/analytics'
import * as firebase from '@firebase/app'
import type { RemoteConfig } from '@firebase/remote-config'
import * as firebaseRemoteConfig from '@firebase/remote-config'
import { renderHook, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useLogNavigation } from 'app/App/hook/useLogNavigation'
import { configureTestStore } from 'commons/store/testUtils'
import type { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { Link, MemoryRouter, Route, Routes } from 'react-router'
import { expect, vi } from 'vitest'

import { firebaseConfig } from '@/commons/config/firebase'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { destroyFirebase, useAnalytics, useFirebase } from '../firebase'

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
  children,
}: {
  isCookieEnabled: boolean
  children?: ReactNode
}): JSX.Element => {
  useFirebase(isCookieEnabled)

  return (
    <>
      <h1>Fake App {isCookieEnabled ? 'yes' : 'no'}</h1>
      {children}
    </>
  )
}

const user = sharedCurrentUserFactory()
const renderFakeApp = ({ isCookieEnabled }: { isCookieEnabled: boolean }) => {
  renderWithProviders(<FakeApp isCookieEnabled={isCookieEnabled} />, {
    user,
  })
}
const mockInitializeAnalytics = vi.fn()
const mockGetAnalytics = vi.fn()
const mockSetUserId = vi.fn()
const mockinitializeApp = vi.fn()

describe('useFirebase', () => {
  beforeEach(async () => {
    vi.spyOn(firebase, 'deleteApp').mockResolvedValue()
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValue(true)
    vi.spyOn(firebaseAnalytics, 'initializeAnalytics').mockImplementation(
      mockInitializeAnalytics
    )
    vi.spyOn(firebaseAnalytics, 'getAnalytics').mockImplementation(
      mockGetAnalytics
    )
    vi.spyOn(firebaseAnalytics, 'setUserId').mockImplementation(mockSetUserId)
    vi.spyOn(firebase, 'initializeApp').mockImplementation(mockinitializeApp)
    await destroyFirebase()
  })

  it('should set logEvent and userId if cookie is set', async () => {
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValueOnce(true)
    vi.spyOn(firebase, 'initializeApp').mockReturnValueOnce({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })
    vi.spyOn(firebaseAnalytics, 'getAnalytics').mockReturnValueOnce(
      'getAnalyticsReturn' as unknown as firebaseAnalytics.Analytics
    )

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockResolvedValueOnce(
      true
    )
    vi.spyOn(firebaseRemoteConfig, 'getAll').mockResolvedValueOnce({
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
  it('should not throw and should keep firebase initialized if Remote Config fails with a storage-open error', async () => {
    vi.spyOn(firebase, 'initializeApp').mockReturnValueOnce({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })

    const storageError = new Error(
      'remoteconfig/storage-open: Error thrown when opening storage.'
    )
    storageError.name = 'FirebaseError'

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockRejectedValueOnce(
      storageError
    )

    renderFakeApp({ isCookieEnabled: true })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).toHaveBeenCalledTimes(1)
    })

    await waitFor(() => {
      expect(firebaseRemoteConfig.fetchAndActivate).toHaveBeenCalledTimes(1)
    })

    await Promise.resolve()

    expect(firebase.deleteApp).not.toHaveBeenCalled()
  })

  it('should not initialize firebase if it is not supported', async () => {
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValueOnce(false)

    renderFakeApp({ isCookieEnabled: true })

    await waitFor(() => {
      expect(firebaseAnalytics.isSupported).toHaveBeenCalledTimes(1)
    })

    expect(firebase.initializeApp).not.toHaveBeenCalled()
  })

  it('should silently swallow InvalidStateError from Remote Config', async () => {
    vi.spyOn(firebase, 'initializeApp').mockReturnValueOnce({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })

    const invalidStateError = new Error('InvalidStateError message')
    invalidStateError.name = 'InvalidStateError'

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockRejectedValueOnce(
      invalidStateError
    )

    renderFakeApp({ isCookieEnabled: true })

    await waitFor(() => {
      expect(firebaseAnalytics.initializeAnalytics).toHaveBeenCalledTimes(1)
    })

    await waitFor(() => {
      expect(firebaseRemoteConfig.fetchAndActivate).toHaveBeenCalledTimes(1)
    })

    await Promise.resolve()

    expect(firebase.deleteApp).not.toHaveBeenCalled()
  })

  const NavigationLogger = (): null => {
    useLogNavigation()
    return null
  }

  it('should keep first logEvent and send it when loaded', async () => {
    vi.spyOn(firebaseAnalytics, 'isSupported').mockResolvedValueOnce(true)
    vi.spyOn(firebase, 'initializeApp').mockReturnValueOnce({
      name: '',
      options: {},
      automaticDataCollectionEnabled: true,
    })
    vi.spyOn(firebaseAnalytics, 'getAnalytics').mockReturnValueOnce(
      'getAnalyticsReturn' as unknown as firebaseAnalytics.Analytics
    )

    vi.spyOn(firebaseRemoteConfig, 'fetchAndActivate').mockResolvedValueOnce(
      true
    )
    vi.spyOn(firebaseRemoteConfig, 'getRemoteConfig').mockResolvedValueOnce(
      {} as RemoteConfig
    )
    vi.spyOn(firebaseRemoteConfig, 'getAll').mockResolvedValueOnce({
      A: {
        asString: () => 'true',
        asBoolean: vi.fn(),
        asNumber: vi.fn(),
        getSource: vi.fn(),
      },
    })

    const store = configureTestStore()
    const wrapper = () => (
      <Provider store={store}>
        <FakeApp isCookieEnabled={true}>
          <MemoryRouter initialEntries={['/route']}>
            <NavigationLogger />
            <Routes>
              <Route
                path="/route"
                element={
                  <span>
                    initial <Link to="/">link</Link>
                  </span>
                }
              />
              <Route path="*" element={<span>other</span>} />
            </Routes>
          </MemoryRouter>
        </FakeApp>
      </Provider>
    )

    const { rerender } = renderHook(() => useAnalytics(), { wrapper })
    expect(firebaseAnalytics.logEvent).not.toHaveBeenCalled()

    await userEvent.click(screen.getByText('link'))

    rerender()

    await waitFor(() => {
      expect(firebaseAnalytics.logEvent).toHaveBeenCalledTimes(2)
    })
  })
})
