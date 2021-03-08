import { computeOfferStatus } from '../computeOfferStatus'

describe('compute offer status', () => {
  describe('when offer is inactive', () => {
    it('should be "validée" if status is validated', () => {
      // Given
      const offer = {
        isActive: false,
        status: 'VALIDATED',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('validée')
    })

    it('should be "refusée" if status is rejected', () => {
      // Given
      const offer = {
        isActive: false,
        status: 'REJECTED',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('refusée')
    })
  })

  describe('when offer is active', () => {
    it('should be "active" when offer is not expired nor sold out', () => {
      // Given
      const offer = {
        isActive: true,
        status: 'ACTIVE',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('active')
    })

    it('should be "expirée" when status is expired', () => {
      // Given
      const offer = {
        isActive: true,
        status: 'EXPIRED',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('expirée')
    })

    it('should be "épuisée" when status is soldout', () => {
      // Given
      const offer = {
        isActive: true,
        status: 'SOLD_OUT',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('épuisée')
    })

    it('should be "validation" when offer is awaiting validation', () => {
      // Given
      const offer = {
        isActive: true,
        status: 'AWAITING',
      }

      // When
      const status = computeOfferStatus(offer)

      // Then
      expect(status).toBe('validation')
    })
  })
})
