import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { FrontendError } from '@/commons/errors/FrontendError'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableEntryFormValues } from '../../schemas'
import { getFieldsSpecs } from '../getFieldsSpecs'

describe('getFieldsSpecs', () => {
  const offerBase = getIndividualOfferFactory()

  describe('when mode is CREATION', () => {
    const mode = OFFER_WIZARD_MODE.CREATION

    it('should return expected specs with an invalid booking limit date', () => {
      const result = getFieldsSpecs({
        entries: [
          {
            activationCodes: [],
            activationCodesExpirationDatetime: '',
            bookingLimitDatetime: '',
            bookingsQuantity: undefined,
            id: undefined,
            label: 'Tarif',
            price: 10,
            quantity: 5,
            offerId: offerBase.id,
            remainingQuantity: null,
          },
        ],
        mode,
        offer: offerBase,
      })

      expect(result.minQuantity).toBe(1)
      expect(result.minExpirationDate).toBeNull()
      expect(result.nowAsDate).toBeInstanceOf(Date)
    })

    it('should throw with empty entries', () => {
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(vi.fn())

      expect(() =>
        getFieldsSpecs({
          entries: [] as PriceTableEntryFormValues[],
          offer: offerBase,
          mode,
        })
      ).toThrow('`entries` is empty.')
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(FrontendError))
    })
  })

  describe('when mode is EDITION', () => {
    const mode = OFFER_WIZARD_MODE.EDITION

    it('should return expected specs with a valid booking limit date', () => {
      const result = getFieldsSpecs({
        entries: [
          {
            activationCodes: [],
            activationCodesExpirationDatetime: '',
            bookingLimitDatetime: '2025-12-24',
            bookingsQuantity: 7,
            id: 55,
            label: 'Tarif',
            price: 10,
            quantity: 99,
            offerId: offerBase.id,
            remainingQuantity: null,
          },
        ],
        mode,
        offer: offerBase,
      })

      expect(result.minQuantity).toBe(7)
      expect(result.minExpirationDate).toBeInstanceOf(Date)
    })

    it('should fallback to a min quantity of 0 when bookings quantity is undefined', () => {
      const result = getFieldsSpecs({
        entries: [
          {
            activationCodes: [],
            activationCodesExpirationDatetime: '',
            bookingLimitDatetime: '2025-12-24',
            bookingsQuantity: undefined,
            id: 99,
            label: 'Tarif',
            price: 10,
            quantity: 3,
            offerId: offerBase.id,
            remainingQuantity: null,
          },
        ],
        mode,
        offer: offerBase,
      })

      expect(result.minQuantity).toBe(0)
    })
  })
})
