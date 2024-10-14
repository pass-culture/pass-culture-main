import { localStorageAvailable } from 'commons/utils/localStorageAvailable'

describe('localStorageAvailable', () => {
  it('should check that localstorage is available', () => {
    expect(localStorageAvailable()).toBeTruthy()
  })

  it('should check that localstorage is not available', () => {
    vi.spyOn(window.localStorage.__proto__, 'setItem').mockImplementationOnce(
      () => {
        throw new DOMException()
      }
    )

    expect(localStorageAvailable()).toBeFalsy()
  })

  it('should check that localstorage is not available on Firefox', () => {
    vi.spyOn(window.localStorage.__proto__, 'setItem').mockImplementationOnce(
      () => {
        throw new DOMException('', 'QuotaExceededError')
      }
    )

    expect(localStorageAvailable()).toBeFalsy()
  })
})
