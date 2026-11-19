import {
  resetStorageAvailabilityCache,
  storageAvailable,
} from '@/commons/utils/storageAvailable'

describe('storageAvailable', () => {
  beforeEach(() => {
    resetStorageAvailabilityCache()
  })

  it('should check that localstorage is available', () => {
    expect(storageAvailable('localStorage')).toBeTruthy()
  })

  it('should check that localstorage is not available', () => {
    vi.spyOn(
      Object.getPrototypeOf(window.localStorage),
      'setItem'
    ).mockImplementationOnce(() => {
      throw new DOMException()
    })

    expect(storageAvailable('localStorage')).toBeFalsy()
  })

  it('should check that localstorage is not available on Firefox', () => {
    vi.spyOn(
      Object.getPrototypeOf(window.localStorage),
      'setItem'
    ).mockImplementationOnce(() => {
      throw new DOMException('', 'QuotaExceededError')
    })

    expect(storageAvailable('localStorage')).toBeFalsy()
  })

  it('should probe each storage type only once', () => {
    const setItemSpy = vi.spyOn(
      Object.getPrototypeOf(window.localStorage),
      'setItem'
    )

    storageAvailable('localStorage')
    storageAvailable('localStorage')
    expect(setItemSpy).toHaveBeenCalledTimes(1)

    storageAvailable('sessionStorage')
    storageAvailable('sessionStorage')
    expect(setItemSpy).toHaveBeenCalledTimes(2)
  })

  it('should cache an unavailable storage', () => {
    vi.spyOn(
      Object.getPrototypeOf(window.localStorage),
      'setItem'
    ).mockImplementationOnce(() => {
      throw new DOMException()
    })

    expect(storageAvailable('localStorage')).toBeFalsy()
    expect(storageAvailable('localStorage')).toBeFalsy()
  })
})
