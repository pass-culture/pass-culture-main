import { act, renderHook } from '@testing-library/react'
import * as router from 'react-router'

import { Consents, LOCAL_STORAGE_DEVICE_ID_KEY } from '../orejimeConfig'

vi.mock('react-router', () => ({
  ...vi.importActual('react-router'),
  useLocation: () => ({
    pathname: '',
    search: '',
    hash: '',
    state: null,
    key: 's',
  }),
}))

vi.mock('uuid', () => ({
  v4: () => 'fake-uuid-v4',
}))

vi.mock('@/commons/utils/sendSentryCustomError', () => ({
  sendSentryCustomError: vi.fn(),
}))

vi.mock('@/commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn(() => true),
}))

vi.mock('../orejimeConfig', async () => {
  const actual =
    await vi.importActual<typeof import('../orejimeConfig')>('../orejimeConfig')
  return {
    ...actual,
    orejimeConfig: { mocked: true },
  }
})

function createMockManager(consents: Record<string, boolean> = {}) {
  const listeners: Array<
    (updated: Record<string, boolean>, all: Record<string, boolean>) => void
  > = []

  return {
    on: vi.fn(
      (
        _event: string,
        callback: (
          updated: Record<string, boolean>,
          all: Record<string, boolean>
        ) => void
      ) => {
        listeners.push(callback)
      }
    ),
    getConsent: vi.fn((key: string) => consents[key] ?? false),
    clearConsents: vi.fn(),
    _listeners: listeners,
  }
}

function setupLoadOrejime(manager: ReturnType<typeof createMockManager>) {
  globalThis.loadOrejime = vi.fn(() => ({ manager }))
}

function mockCookie(value: string) {
  Object.defineProperty(document, 'cookie', { writable: true, value })
}

function mockLocation(pathname: string) {
  vi.spyOn(router, 'useLocation').mockReturnValue({
    pathname,
    search: '',
    hash: '',
    state: null,
    key: 's',
  })
}

describe('useOrejime', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.resetModules()
    localStorage.clear()
    mockCookie('')
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
    delete globalThis.loadOrejime
  })

  async function importUseOrejime() {
    const module = await import('../orejime')
    return module.useOrejime
  }

  describe('on adage-iframe path', () => {
    it('should return both consents as false', async () => {
      mockLocation('/adage-iframe/some-page')
      const useOrejime = await importUseOrejime()

      const { result } = renderHook(() => useOrejime())

      expect(result.current).toEqual({
        consentedToFirebase: false,
        consentedToBeamer: false,
      })
    })

    it('should not call loadOrejime', async () => {
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/adage-iframe/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).not.toHaveBeenCalled()
    })
  })

  describe('when loadOrejime is not available', () => {
    it('should add event listener for orejime-script-loaded', async () => {
      mockLocation('/some-page')
      const addEventSpy = vi.spyOn(globalThis, 'addEventListener')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())

      expect(addEventSpy).toHaveBeenCalledWith(
        'orejime-script-loaded',
        expect.any(Function),
        { once: true }
      )
    })

    it('should remove event listener on cleanup', async () => {
      mockLocation('/some-page')
      const removeEventSpy = vi.spyOn(globalThis, 'removeEventListener')
      const useOrejime = await importUseOrejime()

      const { unmount } = renderHook(() => useOrejime())
      unmount()

      expect(removeEventSpy).toHaveBeenCalledWith(
        'orejime-script-loaded',
        expect.any(Function)
      )
    })

    it('should initialize orejime when script-loaded event fires', async () => {
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())

      const manager = createMockManager({
        [Consents.FIREBASE]: true,
        [Consents.BEAMER]: false,
      })
      setupLoadOrejime(manager)

      await act(() => {
        globalThis.dispatchEvent(new Event('orejime-script-loaded'))
      })
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).toHaveBeenCalled()
    })
  })

  describe('when loadOrejime is available', () => {
    it('should initialize orejime on first load', async () => {
      const manager = createMockManager({
        [Consents.FIREBASE]: true,
        [Consents.BEAMER]: false,
      })
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      const { result } = renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).toHaveBeenCalledWith({ mocked: true })
      expect(manager.on).toHaveBeenCalledWith('update', expect.any(Function))
      expect(result.current).toEqual({
        consentedToFirebase: true,
        consentedToBeamer: false,
      })
    })

    it('should set device ID in localStorage when not present', async () => {
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY)).toBe(
        'fake-uuid-v4'
      )
    })

    it('should not overwrite existing device ID', async () => {
      localStorage.setItem(LOCAL_STORAGE_DEVICE_ID_KEY, 'existing-id')
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY)).toBe(
        'existing-id'
      )
    })

    it('should not set device ID when localStorage is unavailable', async () => {
      const { storageAvailable } = await import(
        '@/commons/utils/storageAvailable'
      )
      vi.mocked(storageAvailable).mockReturnValue(false)
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY)).toBeNull()
    })
  })

  describe('when orejime is already initialized', () => {
    it('should reinitialize when pc-pro-orejime cookie is missing', async () => {
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).toHaveBeenCalledTimes(1)

      mockCookie('')
      mockLocation('/another-page')

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).toHaveBeenCalledTimes(2)
    })

    it('should not reinitialize when pc-pro-orejime cookie is present', async () => {
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).toHaveBeenCalledTimes(1)

      mockCookie('pc-pro-orejime=some-value')
      vi.mocked(globalThis.loadOrejime!).mockClear()
      mockLocation('/another-page')

      renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(globalThis.loadOrejime).not.toHaveBeenCalled()
    })
  })

  describe('consent listener', () => {
    it('should update consents when update event fires with changes', async () => {
      const manager = createMockManager({
        [Consents.FIREBASE]: false,
        [Consents.BEAMER]: false,
      })
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      const { result } = renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(result.current.consentedToFirebase).toBe(false)

      const updateCallback = manager._listeners[0]
      await act(() => {
        updateCallback(
          { [Consents.FIREBASE]: true },
          { [Consents.FIREBASE]: true, [Consents.BEAMER]: true }
        )
      })

      expect(result.current).toEqual({
        consentedToFirebase: true,
        consentedToBeamer: true,
      })
    })

    it('should not update consents when update event fires with empty changes', async () => {
      const manager = createMockManager({
        [Consents.FIREBASE]: true,
        [Consents.BEAMER]: true,
      })
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      const { result } = renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      const updateCallback = manager._listeners[0]
      await act(() => {
        updateCallback(
          {},
          { [Consents.FIREBASE]: false, [Consents.BEAMER]: false }
        )
      })

      expect(result.current).toEqual({
        consentedToFirebase: true,
        consentedToBeamer: true,
      })
    })
  })

  describe('error handling', () => {
    it('should send sentry error and set consents to false on failure', async () => {
      const thrownError = new Error('loadOrejime failed')
      globalThis.loadOrejime = vi.fn(() => {
        throw thrownError
      })
      mockLocation('/some-page')

      const { sendSentryCustomError } = await import(
        '@/commons/utils/sendSentryCustomError'
      )
      const useOrejime = await importUseOrejime()

      const { result } = renderHook(() => useOrejime())
      await act(() => vi.runAllTimers())

      expect(sendSentryCustomError).toHaveBeenCalledWith(thrownError)
      expect(result.current).toEqual({
        consentedToFirebase: false,
        consentedToBeamer: false,
      })
    })
  })

  describe('initOrejimeConsent early return', () => {
    it('should do nothing when loadOrejime becomes unavailable before setTimeout fires', async () => {
      const manager = createMockManager()
      setupLoadOrejime(manager)
      mockLocation('/some-page')
      const useOrejime = await importUseOrejime()

      renderHook(() => useOrejime())

      delete globalThis.loadOrejime

      await act(() => vi.runAllTimers())

      expect(manager.on).not.toHaveBeenCalled()
    })
  })
})
