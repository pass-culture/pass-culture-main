import type { PriceTableFormValues } from '../../schemas'
import { toThingStockCreateBodyModel } from '../toThingStockCreateBodyModel'

describe('toThingStockCreateBodyModel', () => {
  const departementCode = '75'
  const formValuesBase: PriceTableFormValues = {
    entries: [
      {
        offerId: 12,
        label: 'Tarif unique',
        price: 10,
        quantity: 12,
        bookingLimitDatetime: '2022-10-26',
        activationCodes: [],
        activationCodesExpirationDatetime: '',
        bookingsQuantity: undefined,
        id: undefined,
        remainingQuantity: null,
      },
    ],
    isDuo: true,
  }

  it('should serialize create body with offerId', () => {
    const formValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [{ ...formValuesBase.entries[0] }],
    }

    const result = toThingStockCreateBodyModel(formValues, { departementCode })

    expect(result).toStrictEqual({
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
      offerId: 12,
    })
  })

  it('should include activation codes and expiration when provided', () => {
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [
        {
          ...formValuesBase.entries[0],
          activationCodes: ['A', 'B'],
          activationCodesExpirationDatetime: '2022-10-27',
        },
      ],
    }

    const result = toThingStockCreateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.activationCodes).toEqual(['A', 'B'])
    expect(result.activationCodesExpirationDatetime).toBe(
      '2022-10-27T21:59:59Z'
    )
  })

  it('should set bookingLimitDatetime to null when empty', () => {
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [
        {
          ...formValuesBase.entries[0],
          bookingLimitDatetime: '',
        },
      ],
    }

    const result = toThingStockCreateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.bookingLimitDatetime).toBeNull()
  })

  it('should fallback price to 0 and quantity to null', () => {
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [
        {
          ...formValuesBase.entries[0],
          price: 0,
          quantity: undefined as unknown as number,
          activationCodes: [],
          activationCodesExpirationDatetime: '',
        },
      ],
    }

    const result = toThingStockCreateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.price).toBe(0)
    expect(result.quantity).toBeNull()
  })

  it('should not set activationCodesExpirationDatetime when invalid/empty expiration', () => {
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [
        {
          ...formValuesBase.entries[0],
          activationCodes: ['X'],
          activationCodesExpirationDatetime: '',
        },
      ],
    }

    const result = toThingStockCreateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.activationCodes).toEqual(['X'])
    expect(result).not.toHaveProperty('activationCodesExpirationDatetime')
  })
})
