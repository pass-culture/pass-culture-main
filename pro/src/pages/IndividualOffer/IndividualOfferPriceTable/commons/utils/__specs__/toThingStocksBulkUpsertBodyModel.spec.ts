import { format } from 'date-fns'
import { describe, expect, it } from 'vitest'

import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'

import type {
  PriceTableEntryFormValues,
  PriceTableFormValues,
} from '../../schemas'
import { toThingStocksBulkUpsertBodyModel } from '../toThingStocksBulkUpsertBodyModel'

describe('toThingStocksBulkUpsertBodyModel', () => {
  const formValuesEntryBase: PriceTableEntryFormValues = {
    id: null,
    offerId: 42,
    price: 10,
    quantity: 5,
    bookingLimitDatetime: null,
    activationCodes: null,
    activationCodesExpirationDatetime: null,
    bookingsQuantity: null,
    remainingQuantity: null,
    hasActivationCode: false,
    label: 'Tarif',
  }
  const contextBase = { departementCode: '75' }

  it('should map a basic entry without dates or codes', () => {
    const formValues: PriceTableFormValues = {
      entries: [formValuesEntryBase],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks).toHaveLength(1)
    expect(result.stocks[0]).toEqual({
      id: null,
      activationCodes: null,
      activationCodesExpirationDatetime: null,
      bookingLimitDatetime: null,
      offerId: 42,
      price: 10,
      quantity: 5,
    })
  })

  it('should default null price to 0 and null quantity stay null', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          price: null,
          quantity: null,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].price).toBe(0)
    expect(result.stocks[0].quantity).toBeNull()
  })

  it('should produce bookingLimitDatetime when valid date provided', () => {
    const today = format(new Date(), FORMAT_ISO_DATE_ONLY)
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          bookingLimitDatetime: today,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].bookingLimitDatetime).not.toBeNull()
    // Should be an ISO string without milliseconds and ending with 'Z'
    expect(result.stocks[0].bookingLimitDatetime).toMatch(
      /T\d{2}:\d{2}:\d{2}Z$/
    )
  })

  it('should ignore invalid bookingLimitDatetime', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          bookingLimitDatetime: 'invalid-date',
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].bookingLimitDatetime).toBeNull()
  })

  it('should not set activationCodesExpirationDatetime if no codes', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          activationCodes: null,
          activationCodesExpirationDatetime: '2025-12-01',
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, {
      departementCode: '75',
    })

    expect(result.stocks[0].activationCodes).toBeNull()
    expect(result.stocks[0].activationCodesExpirationDatetime).toBeNull()
  })

  it('should set activationCodes and expiration when both valid', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          activationCodes: ['A', 'B'],
          activationCodesExpirationDatetime: '2025-10-26',
          hasActivationCode: true,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].activationCodes).toEqual(['A', 'B'])
    expect(result.stocks[0].activationCodesExpirationDatetime).not.toBeNull()
    expect(result.stocks[0].activationCodesExpirationDatetime).toMatch(
      /2025-10-26T\d{2}:\d{2}:\d{2}Z$/
    )
  })

  it('should NOT set activationCodesExpirationDatetime if invalid date despite codes', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          activationCodes: ['A'],
          activationCodesExpirationDatetime: 'bad-date',
          hasActivationCode: true,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].activationCodes).toEqual(['A'])
    expect(result.stocks[0].activationCodesExpirationDatetime).toBeNull()
  })

  it('should handle multiple entries', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          offerId: 1,
        },
        {
          ...formValuesEntryBase,
          offerId: 2,
          price: null,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks).toHaveLength(2)
    expect(result.stocks[0].offerId).toBe(1)
    expect(result.stocks[1].offerId).toBe(2)
    expect(result.stocks[1].price).toBe(0)
  })

  it('should preserve provided id (update case)', () => {
    const formValues: PriceTableFormValues = {
      entries: [
        {
          ...formValuesEntryBase,
          id: 99,
        },
      ],
      isDuo: null,
    }

    const result = toThingStocksBulkUpsertBodyModel(formValues, contextBase)

    expect(result.stocks[0].id).toBe(99)
  })
})
