import { subDays } from 'date-fns'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableEntryFormValues } from '../../schemas'
import { makeFieldConstraints } from '../makeFieldConstraints'

interface TestCase {
  description: string
  entry: Pick<
    PriceTableEntryFormValues,
    | 'bookingLimitDatetime'
    | 'activationCodesExpirationDatetime'
    | 'bookingsQuantity'
  >
  expected: Omit<
    ReturnType<
      ReturnType<typeof makeFieldConstraints>['computeEntryConstraints']
    >,
    'bookingLimitDatetimeMin' | 'nowAsDate'
  >
}

describe('makeFieldConstraints', () => {
  const offer = getIndividualOfferFactory()

  const baseEntry: Omit<
    PriceTableEntryFormValues,
    | 'bookingLimitDatetime'
    | 'activationCodesExpirationDatetime'
    | 'bookingsQuantity'
  > = {
    activationCodes: [],
    id: undefined,
    label: 'Tarif',
    price: 10,
    quantity: 5,
    offerId: offer.id,
    remainingQuantity: null,
  }

  describe('when mode is CREATION', () => {
    const mode = OFFER_WIZARD_MODE.CREATION

    const creationCases: TestCase[] = [
      {
        description:
          'should handle invalid bookingLimitDatetime and empty expiration',
        entry: {
          activationCodesExpirationDatetime: '',
          bookingLimitDatetime: '',
          bookingsQuantity: undefined,
        },
        expected: {
          activationCodesExpirationDatetimeMin: null,
          bookingLimitDatetimeMax: undefined,
          quantityMin: 1,
        },
      },
      {
        description:
          'should handle valid bookingLimitDatetime + valid expiration date',
        entry: {
          activationCodesExpirationDatetime: '2026-07-10',
          bookingLimitDatetime: '2026-06-20',
          bookingsQuantity: 42, // ignored in CREATION
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2026-06-20'),
          bookingLimitDatetimeMax: subDays(new Date('2026-07-10'), 7),
          quantityMin: 1,
        },
      },
      {
        description:
          'should handle valid bookingLimitDatetime + invalid expiration date',
        entry: {
          activationCodesExpirationDatetime: '',
          bookingLimitDatetime: '2031-01-15',
          bookingsQuantity: undefined,
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2031-01-15'),
          bookingLimitDatetimeMax: undefined,
          quantityMin: 1,
        },
      },
    ]

    it.each(creationCases)('$description', ({ entry, expected }) => {
      const { computeEntryConstraints, nowAsDate } = makeFieldConstraints({
        offer,
        mode,
      })
      const result = computeEntryConstraints({
        ...baseEntry,
        ...entry,
      } as PriceTableEntryFormValues)

      expect(result.activationCodesExpirationDatetimeMin).toEqual(
        expected.activationCodesExpirationDatetimeMin
      )
      expect(result.bookingLimitDatetimeMax).toEqual(
        expected.bookingLimitDatetimeMax
      )
      expect(result.bookingLimitDatetimeMin).toBe(nowAsDate)
      expect(result.quantityMin).toBe(expected.quantityMin)
      expect(result.nowAsDate).toBe(nowAsDate)
    })
  })

  describe('when mode is EDITION', () => {
    const mode = OFFER_WIZARD_MODE.EDITION

    const editionCases: TestCase[] = [
      {
        description: 'should set quantityMin 0 when bookingsQuantity undefined',
        entry: {
          activationCodesExpirationDatetime: '',
          bookingLimitDatetime: '2025-12-24',
          bookingsQuantity: undefined,
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2025-12-24'),
          bookingLimitDatetimeMax: undefined,
          quantityMin: 0,
        },
      },
      {
        description: 'should set quantityMin 0 when bookingsQuantity is 0',
        entry: {
          activationCodesExpirationDatetime: '',
          bookingLimitDatetime: '2026-01-10',
          bookingsQuantity: 0,
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2026-01-10'),
          bookingLimitDatetimeMax: undefined,
          quantityMin: 0,
        },
      },
      {
        description:
          'should set quantityMin equal to bookingsQuantity when positive',
        entry: {
          activationCodesExpirationDatetime: '2030-06-01',
          bookingLimitDatetime: '2030-05-05',
          bookingsQuantity: 7,
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2030-05-05'),
          bookingLimitDatetimeMax: subDays(new Date('2030-06-01'), 7),
          quantityMin: 7,
        },
      },
      {
        description:
          'should set activationCodesExpirationDatetimeMin null when bookingLimitDatetime invalid even if expiration valid',
        entry: {
          activationCodesExpirationDatetime: '2031-09-09',
          bookingLimitDatetime: '',
          bookingsQuantity: 3,
        },
        expected: {
          activationCodesExpirationDatetimeMin: null,
          bookingLimitDatetimeMax: subDays(new Date('2031-09-09'), 7),
          quantityMin: 3,
        },
      },
      {
        description:
          'should set no bookingLimitDatetimeMax when expiration invalid',
        entry: {
          activationCodesExpirationDatetime: '',
          bookingLimitDatetime: '2032-03-12',
          bookingsQuantity: 11,
        },
        expected: {
          activationCodesExpirationDatetimeMin: new Date('2032-03-12'),
          bookingLimitDatetimeMax: undefined,
          quantityMin: 11,
        },
      },
    ]

    it.each(editionCases)('$description', ({ entry, expected }) => {
      const { computeEntryConstraints, nowAsDate } = makeFieldConstraints({
        offer,
        mode,
      })

      const result = computeEntryConstraints({
        ...baseEntry,
        ...entry,
      } as PriceTableEntryFormValues)

      expect(result.activationCodesExpirationDatetimeMin).toEqual(
        expected.activationCodesExpirationDatetimeMin
      )
      expect(result.bookingLimitDatetimeMax).toEqual(
        expected.bookingLimitDatetimeMax
      )
      expect(result.bookingLimitDatetimeMin).toBe(nowAsDate)
      expect(result.quantityMin).toBe(expected.quantityMin)
      expect(result.nowAsDate).toBe(nowAsDate)
    })
  })
})
