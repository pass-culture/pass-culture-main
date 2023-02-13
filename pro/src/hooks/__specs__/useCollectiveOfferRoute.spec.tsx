import { renderHook } from '@testing-library/react-hooks'

import * as getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import * as getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useCollectiveOfferRoute from 'hooks/useCollectiveOfferRoute'

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

describe('useCollectiveOfferRoute', () => {
  it('should set the adapter and id for a template offer', async () => {
    const pathName = '/offre/T-A1/collectif/edition'
    const mockAdapter = jest.fn()
    jest
      .spyOn(getCollectiveOfferTemplateAdapter, 'default')
      .mockImplementation(mockAdapter)
    const { result } = renderHook(() =>
      useCollectiveOfferRoute(pathName, 'T-A1')
    )
    expect(result.current.isTemplate).toEqual(true)
    expect(result.current.offerId).toEqual('A1')
    expect(mockAdapter).toHaveBeenCalledTimes(1)
  })

  it('should set the adapter and id for an offer that is not a template', async () => {
    const pathName = '/offre/A1/collectif/edition'
    const mockAdapter = jest.fn()
    jest
      .spyOn(getCollectiveOfferAdapter, 'default')
      .mockImplementation(mockAdapter)
    const { result } = renderHook(() => useCollectiveOfferRoute(pathName, 'A1'))
    expect(result.current.isTemplate).toEqual(false)
    expect(result.current.offerId).toEqual('A1')
    result.current.loadCollectiveOffer?.('')
    expect(mockAdapter).toHaveBeenCalledTimes(1)
  })

  it('should indicate if a route is part of creation', async () => {
    const pathName = '/offre/creation/collectif/vitrine'
    const { result } = renderHook(() => useCollectiveOfferRoute(pathName))
    expect(result.current.isCreation).toEqual(true)
  })

  it('should indicate if a route is part of edition', async () => {
    const pathName = '/offre/:offerId/collectif/recapitulatif'
    const { result } = renderHook(() =>
      useCollectiveOfferRoute(pathName, 'T-A1')
    )
    expect(result.current.isCreation).toEqual(false)
  })
})
