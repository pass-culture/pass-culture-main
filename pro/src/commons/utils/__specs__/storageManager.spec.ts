import * as z from 'zod'

import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import {
  SESSION_STORAGE_KEY,
  sessionStorageManager,
} from '@/commons/utils/sessionStorageManager'
import type { createStorageManager } from '@/commons/utils/storageManager'

describe.each([
  {
    name: 'localStorageManager',
    manager: localStorageManager,
    getStorage: () => window.localStorage,
    key: LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
  },
  {
    name: 'sessionStorageManager',
    manager: sessionStorageManager,
    getStorage: () => window.sessionStorage,
    key: SESSION_STORAGE_KEY.INDIVIDUAL_OFFERS_FILTER_CONFIG,
  },
] as const)('$name', ({ manager, getStorage, key }) => {
  // The managers are typed with their own key enum: widen it to share the tests.
  const anyKeyManager = manager as ReturnType<
    typeof createStorageManager<string>
  >

  beforeEach(() => {
    getStorage().clear()
  })

  const makeStorageUnavailable = () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementationOnce(() => {
      throw new DOMException('', 'SecurityError')
    })
  }

  it('should report the storage as available', () => {
    expect(anyKeyManager.isAvailable()).toBe(true)
  })

  it('should report the storage as unavailable', () => {
    makeStorageUnavailable()

    expect(anyKeyManager.isAvailable()).toBe(false)
  })

  it('should read, write and remove a string value', () => {
    anyKeyManager.setItem(key, 'value')
    expect(getStorage().getItem(key)).toBe('value')
    expect(anyKeyManager.getItem(key)).toBe('value')

    anyKeyManager.removeItem(key)
    expect(anyKeyManager.getItem(key)).toBeNull()
  })

  it('should not throw when the quota is exceeded', () => {
    // Prime the availability cache before making setItem throw
    expect(anyKeyManager.isAvailable()).toBe(true)
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('', 'QuotaExceededError')
    })

    expect(() => anyKeyManager.setItem(key, 'value')).not.toThrow()
    expect(() => anyKeyManager.setJSON(key, { a: 1 })).not.toThrow()
    expect(anyKeyManager.getItem(key)).toBeNull()
  })

  it('should be a no-op when the storage is unavailable', () => {
    getStorage().setItem(key, '"seed"')
    makeStorageUnavailable()

    expect(anyKeyManager.getItem(key)).toBeNull()
    expect(anyKeyManager.getJSON(key)).toBeNull()

    anyKeyManager.setItem(key, 'new')
    anyKeyManager.setJSON(key, 'new')
    anyKeyManager.removeItem(key)
    anyKeyManager.clear()

    expect(getStorage().getItem(key)).toBe('"seed"')
  })

  it('should remove every key when calling clear', () => {
    getStorage().setItem(key, 'value')
    getStorage().setItem('someOtherKey', 'value')

    anyKeyManager.clear()

    expect(getStorage()).toHaveLength(0)
  })

  describe('getJSON / setJSON', () => {
    it('should write a JSON value and read it back', () => {
      anyKeyManager.setJSON(key, { venueId: 1, tabs: ['a', 'b'] })

      expect(getStorage().getItem(key)).toBe('{"venueId":1,"tabs":["a","b"]}')
      expect(anyKeyManager.getJSON(key)).toEqual({
        venueId: 1,
        tabs: ['a', 'b'],
      })
    })

    it('should return null when the key is missing', () => {
      expect(anyKeyManager.getJSON(key)).toBeNull()
    })

    it('should return null when the stored value is not valid JSON', () => {
      getStorage().setItem(key, '{not json')

      expect(anyKeyManager.getJSON(key)).toBeNull()
    })

    it('should not store a value that cannot be serialized', () => {
      const circular: Record<string, unknown> = {}
      circular.self = circular

      expect(() => anyKeyManager.setJSON(key, circular)).not.toThrow()
      expect(getStorage().getItem(key)).toBeNull()
    })

    describe('with a schema', () => {
      const schema = z.object({ venueId: z.number() })

      it('should return the value when it matches the schema', () => {
        getStorage().setItem(key, '{"venueId":1}')

        expect(anyKeyManager.getJSON(key, schema)).toEqual({ venueId: 1 })
      })

      it('should return null when the value does not match the schema', () => {
        getStorage().setItem(key, '{"venueId":"1"}')

        expect(anyKeyManager.getJSON(key, schema)).toBeNull()
      })
    })
  })
})
