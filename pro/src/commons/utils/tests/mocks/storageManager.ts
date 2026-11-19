import { vi } from 'vitest'

/**
 * In-memory replacement for `localStorageManager` / `sessionStorageManager`,
 * meant to be returned from a `vi.mock` factory.
 *
 * `getStorage` is a getter so that tests can replace the backing `Map` between test cases.
 */
export const createInMemoryStorageManagerMock = (
  getStorage: () => Map<string, string>
) => {
  const getItem = vi.fn((key: string) => getStorage().get(key) ?? null)
  const setItem = vi.fn((key: string, value: string) => {
    getStorage().set(key, value)
  })

  return {
    isAvailable: vi.fn(() => true),
    getItem,
    setItem,
    removeItem: vi.fn((key: string) => {
      getStorage().delete(key)
    }),
    clear: vi.fn(() => {
      getStorage().clear()
    }),
    getJSON: vi.fn((key: string) => {
      const rawValue = getItem(key)
      if (rawValue === null) {
        return null
      }
      try {
        return JSON.parse(rawValue)
      } catch {
        return null
      }
    }),
    setJSON: vi.fn((key: string, value: unknown) => {
      setItem(key, JSON.stringify(value))
    }),
  }
}
