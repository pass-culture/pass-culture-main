import { localStorageManager } from '../localStorageManager'
import * as storageAvailableModule from '../storageAvailable'

vi.mock('../storageAvailable')

describe('localStorageManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should not set item if localStorage is not available', () => {
    const localStorageSetItemSpy = vi.spyOn(
      window.localStorage.__proto__,
      'setItem'
    )
    const storageAvailableSpy = vi
      .spyOn(storageAvailableModule, 'storageAvailable')
      .mockReturnValue(false)

    localStorageManager.setItemIfNone('someKey', 'someValue')

    expect(storageAvailableSpy).toHaveBeenCalledWith('localStorage')
    expect(localStorageSetItemSpy).not.toHaveBeenCalled()
  })

  it('should not set item if localStorage is already set', () => {
    vi.spyOn(window.localStorage.__proto__, 'getItem').mockReturnValueOnce(
      'someValue'
    )
    const localStorageSetItemSpy = vi.spyOn(
      window.localStorage.__proto__,
      'setItem'
    )

    vi.spyOn(storageAvailableModule, 'storageAvailable').mockReturnValue(true)

    localStorageManager.setItemIfNone('someKey', 'someNewValue')

    expect(localStorageSetItemSpy).not.toHaveBeenCalled()
  })

  it('should set the item', () => {
    const localStorageSetItemSpy = vi.spyOn(
      window.localStorage.__proto__,
      'setItem'
    )
    vi.spyOn(storageAvailableModule, 'storageAvailable').mockReturnValue(true)

    localStorageManager.setItemIfNone('someKey', 'someValue')

    expect(localStorageSetItemSpy).toHaveBeenCalled()
  })
})
