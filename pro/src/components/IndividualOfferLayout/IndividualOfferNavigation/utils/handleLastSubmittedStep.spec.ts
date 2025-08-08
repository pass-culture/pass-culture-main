import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'

import {
  cleanLocalStorageAboutLastSubmittedStep,
  getDeprecatedLocalStorageKeyName,
  getLastSubmittedStep,
  getLocalStorageKeyName,
  updateLocalStorageWithLastSubmittedStep,
} from './handleLastSubmittedStep'

describe('handleLastSubmittedStep', () => {
  describe('getLastSubmittedStep', () => {
    it('should return null if offerId is null', () => {
      const result = getLastSubmittedStep(undefined)
      expect(result).toBe(null)
    })

    it('should return null if localStorage is not available', () => {
      vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('LocalStorage not available')
      })

      const result = getLastSubmittedStep('1')
      expect(result).toBe(null)
    })

    it('should return the saved last submitted step if found', () => {
      const savedLastSubmittedStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS
      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(
        savedLastSubmittedStep
      )

      const result = getLastSubmittedStep('1')
      expect(result).toEqual(savedLastSubmittedStep)
      const localStorageKeyName = getLocalStorageKeyName('1')
      expect(Storage.prototype.getItem).toHaveBeenCalledWith(
        localStorageKeyName
      )
    })

    it('should translate the deprecated way to remember that last submitted step = USEFUL_INFORMATIONS', () => {
      // In localStorage, only the deprecated key (USEFUL_INFORMATION_SUBMITTED_${offerId})
      // exists - we expect first getItem to return null.
      const usefulInformationSubmitted = 'true'
      vi.spyOn(Storage.prototype, 'getItem')
        .mockReturnValueOnce(null)
        .mockReturnValueOnce(null)
        .mockReturnValueOnce(usefulInformationSubmitted)

      const keyValueTranslation =
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS

      const result = getLastSubmittedStep('1')
      expect(result).toEqual(keyValueTranslation)
      const localStorageKeyName = getLocalStorageKeyName('1')
      // getItem is also called in storageAvailable(), which makes 3 calls.
      expect(Storage.prototype.getItem).toHaveBeenNthCalledWith(
        2,
        localStorageKeyName
      )
      const deprecatedLocalStorageKeyName =
        getDeprecatedLocalStorageKeyName('1')
      expect(Storage.prototype.getItem).toHaveBeenNthCalledWith(
        3,
        deprecatedLocalStorageKeyName
      )
    })
  })

  describe('updateLocalStorageWithLastSubmittedStep', () => {
    it('should not set anything if localStorage is not available', () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('LocalStorage not available')
      })

      updateLocalStorageWithLastSubmittedStep(
        '1',
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      )

      // Is called once because in storageAvailable(localStorage),
      // we actually call setItem to check if localStorage is available.
      expect(setItemSpy).toHaveBeenCalledOnce()
      const localStorageKeyName = getLocalStorageKeyName('1')
      expect(setItemSpy).not.toHaveBeenCalledWith(
        localStorageKeyName,
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      )
    })

    it('should set the saved last submitted step in appropriate localStorage', () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')

      updateLocalStorageWithLastSubmittedStep(
        '1',
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      )

      const localStorageKeyName = getLocalStorageKeyName('1')
      expect(setItemSpy).toHaveBeenCalledWith(
        localStorageKeyName,
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      )
    })
  })

  describe('cleanLocalStorageAboutLastSubmittedStep', () => {
    it('should not remove anything if localStorage is not available', () => {
      const removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new Error('LocalStorage not available')
      })

      cleanLocalStorageAboutLastSubmittedStep('1')

      expect(removeItemSpy).not.toHaveBeenCalled()
    })

    it('should cleanup appropriate localStorage (new & deprecated keys) regarding last submitted step', () => {
      const removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem')

      cleanLocalStorageAboutLastSubmittedStep('1')

      const localStorageKeyName = getLocalStorageKeyName('1')
      // removeItem is also called in storageAvailable(), which makes 3 calls.
      expect(removeItemSpy).toHaveBeenNthCalledWith(2, localStorageKeyName)
      // Also we expect to cleanup deprecated key.
      const deprecatedLocalStorageKeyName =
        getDeprecatedLocalStorageKeyName('1')
      expect(removeItemSpy).toHaveBeenNthCalledWith(
        3,
        deprecatedLocalStorageKeyName
      )
    })
  })
})
