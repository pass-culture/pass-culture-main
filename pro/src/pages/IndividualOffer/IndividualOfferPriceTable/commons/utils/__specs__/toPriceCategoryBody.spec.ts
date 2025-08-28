import { FrontendError } from '@/commons/errors/FrontendError'

import { toPriceCategoryBody } from '../toPriceCategoryBody'

describe('toPriceCategoryBody', () => {
  const baseFormValues = {
    entries: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: '',
        bookingLimitDatetime: '',
        bookingsQuantity: undefined,
        id: undefined,
        label: 'Normal',
        price: 10,
        quantity: 5,
        offerId: 1,
        remainingQuantity: null,
      },
    ],
    isDuo: true as boolean | null,
  }

  it('should map entries without id', () => {
    const formValues = baseFormValues

    const result = toPriceCategoryBody(formValues)

    expect(result).toEqual({
      priceCategories: [{ label: 'Normal', price: 10 }],
    })
  })

  it('should keep id when provided', () => {
    const formValues = {
      ...baseFormValues,
      entries: [{ ...baseFormValues.entries[0], id: 99 }],
    }

    const result = toPriceCategoryBody(formValues)

    expect(result).toEqual({
      priceCategories: [{ id: 99, label: 'Normal', price: 10 }],
    })
  })

  it('should throw when label missing', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    const formValues = {
      ...baseFormValues,
      entries: [{ ...baseFormValues.entries[0], label: '' }],
    }

    const call = () => toPriceCategoryBody(formValues)

    expect(call).toThrow('`entry.label` is undefined.')
    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(FrontendError))
  })
})
