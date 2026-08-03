import type { LOCAL_STORAGE_KEY as LocalStorageKeyType } from 'commons/utils/localStorageManager'
import {
  saveActivityToStorage,
  saveOpenToPublicToStorage,
  saveSiretToStorage,
  saveTargetAudienceToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from 'pages/Simulator/storage'
import { vi } from 'vitest'

import { ActivityOpenToPublic } from 'apiClient/v1'

const inMemoryLocalStorage = new Map<string, string>()

vi.mock('@/commons/utils/localStorageManager', async () => {
  const actual = await vi.importActual('@/commons/utils/localStorageManager')

  return {
    ...actual,
    localStorageManager: {
      getItem: vi.fn((key: LocalStorageKeyType) => {
        return inMemoryLocalStorage.get(key) ?? null
      }),
      setItem: vi.fn((key: LocalStorageKeyType, value: string) => {
        inMemoryLocalStorage.set(key, value)
      }),
    },
  }
})
const mockSetSiret = vi.fn()
const mockSetOpenToPublic = vi.fn()
const mockSetTargetAudience = vi.fn()
const mockSetActivity = vi.fn()

describe('storage', () => {
  it('should save and retrieve siret', () => {
    const initialValue = tryRestoreSiretFromStorage(mockSetSiret)
    expect(initialValue).toBeUndefined()
    expect(mockSetSiret).not.toHaveBeenCalled()
    saveSiretToStorage('12312312312312')
    const storedValue = tryRestoreSiretFromStorage(mockSetSiret)
    expect(storedValue).toBe('12312312312312')
    expect(mockSetSiret).toHaveBeenCalledWith('12312312312312')
  })

  it('should save and retrieve open to public', () => {
    const initialValue = tryRestoreOpenToPublicFromStorage(mockSetOpenToPublic)
    expect(initialValue).toBeUndefined()
    expect(mockSetOpenToPublic).not.toHaveBeenCalled()
    saveOpenToPublicToStorage('true')
    const storedValue = tryRestoreOpenToPublicFromStorage(mockSetOpenToPublic)
    expect(storedValue).toBe('true')
    expect(mockSetOpenToPublic).toHaveBeenCalledWith('true')
  })

  it('should save and retrieve activity', () => {
    const initialValue = tryRestoreActivityFromStorage(mockSetActivity)
    expect(initialValue).toBeUndefined()
    expect(mockSetActivity).not.toHaveBeenCalled()
    saveActivityToStorage(ActivityOpenToPublic.ART_GALLERY)
    const storedValue = tryRestoreActivityFromStorage(mockSetActivity)
    expect(storedValue).toBe(ActivityOpenToPublic.ART_GALLERY)
    expect(mockSetActivity).toHaveBeenCalledWith(
      ActivityOpenToPublic.ART_GALLERY
    )
  })

  it('should save and retrieve target customer', () => {
    const initialValue = tryRestoreTargetAudienceFromStorage(
      mockSetTargetAudience
    )
    expect(initialValue).toBeUndefined()
    expect(mockSetTargetAudience).not.toHaveBeenCalled()
    saveTargetAudienceToStorage({ individual: true })
    const storedValue = tryRestoreTargetAudienceFromStorage(
      mockSetTargetAudience
    )
    expect(storedValue).toEqual({ individual: true })
    expect(mockSetTargetAudience).toHaveBeenCalledWith({ individual: true })
  })
})
