import { renderHook, waitFor } from '@testing-library/react'
import * as router from 'react-router'

import { api } from 'apiClient/api'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'

import { useCollectiveOfferFromParams } from '../useCollectiveOfferFromParams'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: () => ({
    pathname: 'vitrine',
  }),
}))

describe('useCollectiveOfferFromParams', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
  })

  it('should retrieve a template offer from the url', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    const getCollectiveOfferTemplateSpy = vi
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValueOnce(offer)

    const { result } = renderHook(() =>
      useCollectiveOfferFromParams(true, '10')
    )

    //  Wait for the second render following the reception of the template offer
    await waitFor(() =>
      expect(getCollectiveOfferTemplateSpy).toHaveBeenCalled()
    )

    expect(result.current.offer?.name).toEqual(offer.name)
  })

  it('should retrieve a bookable offer from the url', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      pathname: '',
      state: {},
      hash: '',
      key: '',
      search: '',
    })

    const offer = getCollectiveOfferFactory()
    const getCollectiveOfferSpy = vi
      .spyOn(api, 'getCollectiveOffer')
      .mockResolvedValueOnce(offer)

    const { result } = renderHook(() =>
      useCollectiveOfferFromParams(false, '10')
    )

    //  Wait for the second render following the reception of the bookable offer
    await waitFor(() => expect(getCollectiveOfferSpy).toHaveBeenCalled())

    expect(result.current.offer?.name).toEqual(offer.name)
  })

  it('should return undefined when there are no offerId in the params', () => {
    const { result } = renderHook(() =>
      useCollectiveOfferFromParams(false, undefined)
    )

    expect(result.current.offer).toEqual(undefined)
  })

  it('should return undefined when the offerId in the params is an invalid number', () => {
    const { result } = renderHook(() =>
      useCollectiveOfferFromParams(false, 'abcd')
    )

    expect(result.current.offer).toEqual(undefined)
  })
})
