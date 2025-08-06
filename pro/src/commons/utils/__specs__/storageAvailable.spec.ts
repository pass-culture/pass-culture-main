import { storageAvailable } from '@/commons/utils/storageAvailable'

describe('storageAvailable', () => {
  it('should check that localstorage is available', () => {
    expect(storageAvailable('localStorage')).toBeTruthy()
  })

  it('should check that localstorage is not available', () => {
    vi.spyOn(window.localStorage.__proto__, 'setItem').mockImplementationOnce(
      () => {
        throw new DOMException()
      }
    )

    expect(storageAvailable('localStorage')).toBeFalsy()
  })

  it('should check that localstorage is not available on Firefox', () => {
    vi.spyOn(window.localStorage.__proto__, 'setItem').mockImplementationOnce(
      () => {
        throw new DOMException('', 'QuotaExceededError')
      }
    )

    expect(storageAvailable('localStorage')).toBeFalsy()
  })
})
