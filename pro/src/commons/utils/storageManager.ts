import * as z from 'zod'

import { type StorageType, storageAvailable } from './storageAvailable'

/**
 * Builds a safe wrapper around a Web Storage (`localStorage` or `sessionStorage`).
 *
 * Every method is a no-op (or returns `null`) when the storage is unavailable
 * (private browsing, blocked cookies, sandboxed iframe…) and never throws.
 *
 * Do not use it directly: use `localStorageManager` or `sessionStorageManager`.
 */
export const createStorageManager = <K extends string>(type: StorageType) => {
  const getStorage = (): Storage | null =>
    storageAvailable(type) ? globalThis[type] : null

  const getItem = (key: K): string | null => {
    try {
      return getStorage()?.getItem(key) ?? null
    } catch {
      return null
    }
  }

  const setItem = (key: K, value: string): void => {
    try {
      getStorage()?.setItem(key, value)
    } catch {
      // Quota exceeded: the value is not persisted, the app keeps working.
    }
  }

  const removeItem = (key: K): void => {
    try {
      getStorage()?.removeItem(key)
    } catch {
      // Nothing to do: the key is unreachable anyway.
    }
  }

  return {
    isAvailable: (): boolean => storageAvailable(type),

    getItem,

    setItem,

    removeItem,

    clear: (): void => {
      try {
        getStorage()?.clear()
      } catch {
        // Nothing to do: the storage is unreachable anyway.
      }
    },

    /**
     * Reads and parses a JSON value.
     *
     * Returns `null` when the key is missing, when the stored value is not valid JSON,
     * or when it does not match the optional `schema`.
     * Without `schema`, the parsed value is trusted to be a `T` (not validated).
     */
    getJSON: <T>(key: K, schema?: z.core.$ZodType<T>): T | null => {
      const rawValue = getItem(key)
      if (rawValue === null) {
        return null
      }

      let parsedValue: unknown
      try {
        parsedValue = JSON.parse(rawValue)
      } catch {
        return null
      }

      if (!schema) {
        return parsedValue as T
      }

      const result = z.safeParse(schema, parsedValue)
      return result.success ? result.data : null
    },

    /**
     * Serializes a value to JSON and stores it.
     * Serialization errors (circular references, BigInt) are ignored, like storage errors.
     */
    setJSON: <T>(key: K, value: T): void => {
      let serializedValue: string
      try {
        serializedValue = JSON.stringify(value)
      } catch {
        return
      }

      setItem(key, serializedValue)
    },
  }
}
