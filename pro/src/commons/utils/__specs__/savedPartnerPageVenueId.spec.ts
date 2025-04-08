import {
  SAVED_HOME_PAGE_VENUE_ID_KEYS,
  SAVED_PARTNER_PAGE_VENUE_ID_KEYS,
  getSavedPartnerPageVenueId,
  setSavedPartnerPageVenueId,
} from '../savedPartnerPageVenueId'

describe('savedPartnerPageVenueId', () => {
  describe('getSavedPartnerPageVenueId', () => {
    it('should return an empty string if offererId is null', () => {
      const result = getSavedPartnerPageVenueId('homepage', null)
      expect(result).toBe(undefined)
    })

    it('should return an empty string if localStorage is not available', () => {
      vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('LocalStorage not available')
      })

      const result = getSavedPartnerPageVenueId('homepage', 1)
      expect(result).toBe(undefined)
    })

    it('should return an empty string if no saved venue id found', () => {
      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue('{}')
      const result = getSavedPartnerPageVenueId('homepage', 1)
      expect(result).toBe(undefined)
    })

    it('should return the saved venue id if found', () => {
      const savedVenues = { 1: '123' }
      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(
        JSON.stringify(savedVenues)
      )
      const result = getSavedPartnerPageVenueId('homepage', 1)
      expect(result).toBe('123')
    })
  })

  describe('setSavedPartnerPageVenueId', () => {
    it('should not set anything if offererId is null', () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      setSavedPartnerPageVenueId('homepage', null, '123')
      expect(setItemSpy).not.toHaveBeenCalled()
    })

    it('should not set anything if localStorage is not available', () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('LocalStorage not available')
      })
      setSavedPartnerPageVenueId('homepage', 1, '123')

      // Is called once because in storageAvailable(localStorage),
      // we actually call setItem to check if localStorage is available.
      expect(setItemSpy).toHaveBeenCalledOnce()
      expect(setItemSpy).not.toHaveBeenCalledWith(
        SAVED_HOME_PAGE_VENUE_ID_KEYS,
        JSON.stringify({ 1: '123' })
      )
    })

    it('should set the saved venue id in appropriate localStorage', () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      const savedVenues = { 1: '123' }
      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(
        JSON.stringify(savedVenues)
      )

      // First we set a venue id from homepage.
      setSavedPartnerPageVenueId('homepage', 1, '456')
      expect(setItemSpy).toHaveBeenCalledWith(
        SAVED_HOME_PAGE_VENUE_ID_KEYS,
        JSON.stringify({ 1: '456' })
      )

      // Then we set a venue id from partnerPage.
      setSavedPartnerPageVenueId('partnerPage', 1, '789')
      expect(setItemSpy).toHaveBeenCalledWith(
        SAVED_PARTNER_PAGE_VENUE_ID_KEYS,
        JSON.stringify({ 1: '789' })
      )
    })
  })
})
