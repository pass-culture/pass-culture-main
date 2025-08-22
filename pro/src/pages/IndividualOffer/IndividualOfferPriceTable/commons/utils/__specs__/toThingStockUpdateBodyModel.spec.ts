import type { PriceTableFormValues } from '../../schemas'
import { toThingStockUpdateBodyModel } from '../toThingStockUpdateBodyModel'

describe('toThingStockUpdateBodyModel', () => {
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

  it('should serialize update body', () => {
    const formValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [{ ...formValuesBase.entries[0] }],
    }

    const result = toThingStockUpdateBodyModel(formValues, { departementCode })

    expect(result).toStrictEqual({
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
    })
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

    const result = toThingStockUpdateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.bookingLimitDatetime).toBeNull()
  })

  it('should keep quantity 0', () => {
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [
        {
          ...formValuesBase.entries[0],
          quantity: 0,
        },
      ],
    }

    const result = toThingStockUpdateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.quantity).toBe(0)
  })

  it('should set quantity to null when undefined', () => {
    const { quantity: _removed, ...entryWithoutQuantity } =
      formValuesBase.entries[0]
    const localFormValues: PriceTableFormValues = {
      ...formValuesBase,
      entries: [entryWithoutQuantity as (typeof formValuesBase.entries)[0]],
    }

    const result = toThingStockUpdateBodyModel(localFormValues, {
      departementCode,
    })

    expect(result.quantity).toBeNull()
  })
})
