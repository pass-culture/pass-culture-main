import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as handleErrorModule from '@/commons/errors/handleError'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import { logout } from '../logout'

vi.mock('@/apiClient/api', () => ({
  api: {
    signout: vi.fn(),
  },
}))
vi.mock('@/commons/errors/handleError', () => ({
  handleError: vi.fn(),
}))

describe('logout', () => {
  const windowLocationHrefMock = vi.fn()

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()

    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      get href() {
        return windowLocationHrefMock()
      },
      set href(value: string) {
        windowLocationHrefMock(value)
      },
    })

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '1')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '2')
  })

  it('should call signout, clear localStorage, and reset related slices when shouldCallSignout=true', async () => {
    const sucessfulFetchMock = vi.fn(() => Promise.resolve(new Response()))
    vi.spyOn(window, 'fetch').mockImplementation(sucessfulFetchMock)

    await logout()

    expect(sucessfulFetchMock).toHaveBeenNthCalledWith(
      1,
      expect.stringMatching(/\/users\/signout$/),
      { credentials: 'include' }
    )
    expect(windowLocationHrefMock).toHaveBeenCalledExactlyOnceWith('/connexion')

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should handle signout error gracefully and still reset state', async () => {
    const failedFetchMock = vi.fn(() => Promise.reject(new Error()))
    vi.spyOn(window, 'fetch').mockImplementation(failedFetchMock)
    vi.spyOn(api, 'signout').mockRejectedValue(new Error())
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')

    await logout()

    expect(handleErrorSpy).toHaveBeenCalledWith(
      expect.any(Error),
      'Une erreur est survenue lors de la déconnexion.'
    )
    expect(windowLocationHrefMock).toHaveBeenCalledExactlyOnceWith('/connexion')

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })
})
