import { describe, expect, it, vi } from 'vitest'

import type { GetOffererResponseModel } from '@/apiClient/v1/models/GetOffererResponseModel'

import { defaultGetOffererResponseModel } from '../factories/individualApiFactories'
import { getOffererData } from '../offererStoreHelper'

const mockOfferer: GetOffererResponseModel = {
  ...defaultGetOffererResponseModel,
  id: 42,
}

describe('getOffererData', () => {
  it('returns currentOfferer if id matches', async () => {
    const apiCall = vi.fn()
    const result = await getOffererData(42, mockOfferer, apiCall)
    expect(result).toBe(mockOfferer)
    expect(apiCall).not.toHaveBeenCalled()
  })

  it('calls apiCall if id does not match', async () => {
    const apiCall = vi
      .fn()
      .mockResolvedValue({ id: 99 } as GetOffererResponseModel)
    const result = await getOffererData(99, mockOfferer, apiCall)
    expect(result).toEqual({ id: 99 })
    expect(apiCall).toHaveBeenCalled()
  })

  it('calls apiCall if currentOfferer is null', async () => {
    const apiCall = vi
      .fn()
      .mockResolvedValue({ id: 123 } as GetOffererResponseModel)
    const result = await getOffererData(123, null, apiCall)
    expect(result).toEqual({ id: 123 })
    expect(apiCall).toHaveBeenCalled()
  })

  it('returns null if requestedOffererId is null', async () => {
    const apiCall = vi.fn()
    const result = await getOffererData(null, mockOfferer, apiCall)
    expect(result).toBeNull()
    expect(apiCall).not.toHaveBeenCalled()
  })

  it('calls apiCall if currentOfferer is undefined', async () => {
    const apiCall = vi
      .fn()
      .mockResolvedValue({ id: 7 } as GetOffererResponseModel)
    const result = await getOffererData(7, undefined, apiCall)
    expect(result).toEqual({ id: 7 })
    expect(apiCall).toHaveBeenCalled()
  })

  it('calls apiCall if requestedOffererId is undefined', async () => {
    const apiCall = vi.fn()
    const result = await getOffererData(undefined, mockOfferer, apiCall)
    expect(result).toBeUndefined()
    expect(apiCall).toHaveBeenCalled()
  })

  it('returns null if requestedOffererId is null', async () => {
    const apiCall = vi.fn()
    const result = await getOffererData(null, mockOfferer, apiCall)
    expect(result).toBeNull()
    expect(apiCall).not.toHaveBeenCalled()
  })
})
