import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { saveNonEventOfferPriceTable } from '../saveNonEventOfferPriceTable'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
    updateThingStock: vi.fn(),
    createThingStock: vi.fn(),
    getOffer: vi.fn(),
    getStocks: vi.fn(),
  },
}))
vi.mock('@/apiClient/helpers', () => ({
  isErrorAPIError: vi.fn(() => true),
  serializeApiErrors: vi.fn(() => ({ foo: 'Bar', priceLimitationRule: 'X' })),
}))

import { api } from '@/apiClient/api'
import * as helpersModule from '@/apiClient/helpers'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'

// Do not spy on internal utils (handleError, transformers); treat as black box

describe('saveNonEventOfferPriceTable', () => {
  const offer = getIndividualOfferFactory()
  const entryBase = {
    activationCodes: [],
    activationCodesExpirationDatetime: '',
    bookingLimitDatetime: '',
    bookingsQuantity: undefined,
    id: undefined,
    label: 'Normal',
    price: 10,
    quantity: 5,
    offerId: offer.id,
    remainingQuantity: null,
  }
  const formValuesBase = {
    entries: [entryBase],
    isDuo: true,
  }

  it('should create thing stock when first entry has no id', async () => {
    const setError = vi.fn()

    await saveNonEventOfferPriceTable(formValuesBase, {
      offer,
      setError,
    })

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
    expect(api.createThingStock).toHaveBeenCalledWith(
      expect.objectContaining({ offerId: offer.id })
    )
    expect(api.getOffer).toHaveBeenCalledWith(offer.id)
    expect(api.getStocks).toHaveBeenCalledWith(offer.id)
  })

  it('should update thing stock when first entry has id', async () => {
    const formValues = {
      entries: [{ ...entryBase, id: 99 }],
      isDuo: true as boolean | null,
    }
    const setError = vi.fn()

    await saveNonEventOfferPriceTable(formValues, {
      offer,
      setError,
    })

    expect(api.updateThingStock).toHaveBeenCalledWith(99, expect.any(Object))
  })

  it('should set field errors when API error returned', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())
    vi.spyOn(api, 'patchOffer').mockRejectedValueOnce({
      body: { issues: [] },
    })

    const setError = vi.fn()

    await saveNonEventOfferPriceTable(formValuesBase, {
      offer,
      setError,
    })

    expect(isErrorAPIError).toHaveBeenCalled()
    expect(serializeApiErrors).toHaveBeenCalled()
    expect(setError).toHaveBeenCalledWith(
      'foo',
      expect.objectContaining({ message: 'Bar' })
    )
    expect(setError).toHaveBeenCalledWith(
      'entries.0.price',
      expect.objectContaining({ message: 'Non valide' })
    )
    expect(api.getOffer).not.toHaveBeenCalled()
    expect(api.getStocks).not.toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalled()
  })

  it('should set field errors joining array values and skip price limitation rule when absent', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())
    vi.spyOn(api, 'patchOffer').mockRejectedValueOnce({
      body: { issues: [] },
    })
    vi.spyOn(helpersModule, 'serializeApiErrors').mockReturnValueOnce({
      bar: ['Alpha', 'Beta'],
    })

    const setError = vi.fn()

    await saveNonEventOfferPriceTable(formValuesBase, {
      offer,
      setError,
    })

    expect(setError).toHaveBeenCalledWith(
      'bar',
      expect.objectContaining({ message: 'Alpha,  Beta' })
    )
    expect(setError).not.toHaveBeenCalledWith(
      'entries.0.price',
      expect.anything()
    )
    expect(consoleErrorSpy).toHaveBeenCalled()
  })

  it('should delegate non API errors to handleError without setError calls', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())
    vi.spyOn(api, 'patchOffer').mockRejectedValueOnce(new Error('boom'))
    vi.spyOn(helpersModule, 'isErrorAPIError').mockReturnValue(false)

    const setError = vi.fn()

    await saveNonEventOfferPriceTable(formValuesBase, {
      offer,
      setError,
    })

    expect(setError).not.toHaveBeenCalled()
    expect(api.getOffer).not.toHaveBeenCalled()
    expect(api.getStocks).not.toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalled()
  })
})
