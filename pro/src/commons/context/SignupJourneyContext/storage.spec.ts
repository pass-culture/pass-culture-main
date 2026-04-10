import { beforeEach, describe, expect, it, vi } from 'vitest'

import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import type {
  ActivityContext,
  InitialAddress,
  Offerer,
} from './SignupJourneyContext'

const inMemoryLocalStorage = new Map<string, string>()

vi.mock('@/commons/utils/localStorageManager', async () => {
  const actual = await vi.importActual('@/commons/utils/localStorageManager')

  return {
    ...actual,
    localStorageManager: {
      getItem: vi.fn((key: LOCAL_STORAGE_KEY) => {
        return inMemoryLocalStorage.get(key) ?? null
      }),
      setItem: vi.fn((key: LOCAL_STORAGE_KEY, value: string) => {
        inMemoryLocalStorage.set(key, value)
      }),
      removeItem: vi.fn((key: LOCAL_STORAGE_KEY) => {
        inMemoryLocalStorage.delete(key)
      }),
      clearPassCultureKeys: vi.fn(() => {
        inMemoryLocalStorage.clear()
      }),
    },
  }
})

import {
  cleanSignupJourneyStorage,
  RESTORE_ERRORS,
  saveActivityToStorage,
  saveInitialAddressToStorage,
  saveOffererToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from './storage'

describe('SignupJourney storage', () => {
  beforeEach(() => {
    inMemoryLocalStorage.clear()
    vi.clearAllMocks()
  })

  it('should restore offerer from storage', () => {
    const offerer = { hasVenueWithSiret: true, isDiffusible: false } as Offerer
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify(offerer)
    )

    const setOfferer = vi.fn()
    const restored = tryRestoreOffererFromStorage(setOfferer)

    expect(restored).toEqual(offerer)
    expect(setOfferer).toHaveBeenCalledWith(offerer)
  })

  it('should throw when restoring offerer without storage data', () => {
    expect(() => tryRestoreOffererFromStorage(vi.fn())).toThrow(
      RESTORE_ERRORS.NO_OFFERER_DATA_IN_STORAGE
    )
  })

  it('should restore initial address from storage', () => {
    const initialAddress = {
      addressAutocomplete: '1 rue de Paris',
      'search-addressAutocomplete': '1 rue de Paris',
    } as InitialAddress
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS,
      JSON.stringify(initialAddress)
    )

    const setInitialAddress = vi.fn()
    const restored = tryRestoreInitialAddressFromStorage(setInitialAddress)

    expect(restored).toEqual(initialAddress)
    expect(setInitialAddress).toHaveBeenCalledWith(initialAddress)
  })

  it('should throw when restoring initial address without storage data', () => {
    expect(() => tryRestoreInitialAddressFromStorage(vi.fn())).toThrow(
      RESTORE_ERRORS.NO_INITIAL_ADDRESS_DATA_IN_STORAGE
    )
  })

  it('should restore activity from storage', () => {
    const activity = {
      socialUrls: ['https://example.com'],
      targetCustomer: null,
    } as unknown as ActivityContext
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY,
      JSON.stringify(activity)
    )

    const setActivity = vi.fn()
    const restored = tryRestoreActivityFromStorage(setActivity)

    expect(restored).toEqual(activity)
    expect(setActivity).toHaveBeenCalledWith(activity)
  })

  it('should throw when restoring activity without storage data', () => {
    expect(() => tryRestoreActivityFromStorage(vi.fn())).toThrow(
      RESTORE_ERRORS.NO_ACTIVITY_DATA_IN_STORAGE
    )
  })

  it('should save offerer to storage', () => {
    const offerer = { hasVenueWithSiret: false, isDiffusible: true } as Offerer

    saveOffererToStorage(offerer)

    expect(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER)
    ).toBe(JSON.stringify(offerer))
  })

  it('should save initial address to storage', () => {
    const initialAddress = {
      addressAutocomplete: '10 avenue de France',
      'search-addressAutocomplete': '10 avenue de France',
    } as InitialAddress

    saveInitialAddressToStorage(initialAddress)

    expect(
      inMemoryLocalStorage.get(
        LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
      )
    ).toBe(JSON.stringify(initialAddress))
  })

  it('should save activity to storage', () => {
    const activity = {
      socialUrls: [],
      targetCustomer: undefined,
    } as unknown as ActivityContext

    saveActivityToStorage(activity)

    expect(
      inMemoryLocalStorage.get(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
    ).toBe(JSON.stringify(activity))
  })

  it('should clean signup journey storage keys', () => {
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER,
      JSON.stringify({ hasVenueWithSiret: true, isDiffusible: false })
    )
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS,
      JSON.stringify({
        addressAutocomplete: 'x',
        'search-addressAutocomplete': 'x',
      })
    )
    inMemoryLocalStorage.set(
      LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY,
      JSON.stringify({ socialUrls: [], targetCustomer: null })
    )
    inMemoryLocalStorage.set('SOME_OTHER_KEY', 'keep')

    cleanSignupJourneyStorage()

    expect(
      inMemoryLocalStorage.has(LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER)
    ).toBe(false)
    expect(
      inMemoryLocalStorage.has(
        LOCAL_STORAGE_KEY.NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS
      )
    ).toBe(false)
    expect(
      inMemoryLocalStorage.has(LOCAL_STORAGE_KEY.NEW_STRUCTURE_ACTIVITY)
    ).toBe(false)
    expect(inMemoryLocalStorage.get('SOME_OTHER_KEY')).toBe('keep')
  })
})
