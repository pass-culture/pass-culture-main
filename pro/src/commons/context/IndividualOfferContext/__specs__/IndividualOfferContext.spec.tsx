import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { useParams } from 'react-router'
import { SWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { offerVenueFactory } from '@/commons/utils/factories/venueFactories'
import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import {
  IndividualOfferContextProvider,
  useIndividualOfferContext,
} from '../IndividualOfferContext'

const mockNavigate = vi.fn()

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
  useParams: vi.fn(),
  useNavigate: () => mockNavigate,
}))

const renderUseIndividualOfferContext = async () => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <SWRConfig
      value={{
        // Ensure a fresh, isolated cache per test run
        provider: () => new Map(),
        dedupingInterval: 0,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
        shouldRetryOnError: false,
      }}
    >
      <IndividualOfferContextProvider>
        {children}
      </IndividualOfferContextProvider>
    </SWRConfig>
  )

  const { rerender, result, unmount } = renderHook(
    () => useIndividualOfferContext(),
    {
      wrapper,
    }
  )

  await waitFor(() => expect(result.current).not.toBeNull())

  return { rerender, result, unmount }
}

describe('IndividualOfferContextProvider', () => {
  const offerBase = getIndividualOfferFactory({
    id: 1,
    isEvent: false,
  })

  beforeEach(() => {
    vi.spyOn(api, 'getActiveVenueOfferByEan')
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: MOCKED_CATEGORIES,
      subcategories: MOCKED_SUBCATEGORIES,
    })
    vi.spyOn(api, 'getOffer')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe.each([
    ['when there is no offerId in the URL path', {}],
    ['when offerId = "creation" in the URL path', { offerId: 'creation' }],
  ])('%s', (_, pathParams) => {
    beforeEach(() => {
      vi.clearAllMocks()

      vi.mocked(useParams).mockReturnValue(pathParams)
    })

    it('should call the expected api endpoints and return the expected context values', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(api.getOffer).not.toHaveBeenCalled()
      expect(api.getCategories).toHaveBeenCalledOnce()
      expect(api.getActiveVenueOfferByEan).not.toHaveBeenCalled()

      expect(result.current.categories.length).toBeGreaterThan(0)
      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
      expect(result.current.isEvent).toBeNull()
      expect(result.current.offer).toBeNull()
      expect(result.current.offerId).toBeNull()
      expect(result.current.subCategories.length).toBeGreaterThan(0)
    })

    it('should control isEvent via setIsEvent', async () => {
      vi.mocked(useParams).mockReturnValue({
        offerId: 'creation',
      } as unknown as ReturnType<typeof useParams>)

      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isEvent).toBeNull()
      expect(result.current.offerId).toBeNull()

      await waitFor(() => void result.current.setIsEvent(true))

      expect(result.current.isEvent).toBe(true)
      expect(result.current.offerId).toBeNull()
    })

    it('should allow toggling isAccessibilityFilled via setter', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isAccessibilityFilled).toBe(true)

      await waitFor(() => void result.current.setIsAccessibilityFilled(false))

      expect(result.current.isAccessibilityFilled).toBe(false)
    })
  })

  describe('when there is an offerId in the URL', () => {
    beforeEach(() => {
      vi.mocked(useParams).mockReturnValue({
        offerId: '1',
      })
      vi.spyOn(api, 'getOffer').mockResolvedValue(offerBase)
    })

    it('should call the expected api endpoints and return the expected context values', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(api.getOffer).toHaveBeenCalledExactlyOnceWith(1)
      expect(api.getCategories).toHaveBeenCalledOnce()
      expect(api.getActiveVenueOfferByEan).not.toHaveBeenCalled() // because `offerBase` doesn't meet EAN check criteria

      expect(result.current.categories.length).toBeGreaterThan(0)
      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
      expect(result.current.isEvent).toBe(false)
      expect(result.current.offer?.id).toBe(1)
      expect(result.current.offerId).toBe(1)
      expect(result.current.subCategories.length).toBeGreaterThan(0)
    })

    it('should redirect to an error page when the offer does not exist', async () => {
      vi.spyOn(api, 'getOffer').mockRejectedValueOnce({
        status: 404,
      })

      await renderUseIndividualOfferContext()

      expect(mockNavigate).toHaveBeenLastCalledWith('/404', {
        state: { from: 'offer' },
      })
    })

    it('should check for EAN duplicate and set hasPublishedOfferWithSameEan to true when there is one', async () => {
      vi.spyOn(api, 'getOffer').mockResolvedValueOnce({
        ...offerBase,
        extraData: { ean: 2 },
        productId: 3,
        venue: offerVenueFactory({ id: 4 }),
      })
      vi.spyOn(api, 'getActiveVenueOfferByEan').mockResolvedValueOnce({
        ...offerBase,
        id: 5,
      })

      const { result } = await renderUseIndividualOfferContext()

      expect(api.getOffer).toHaveBeenCalledExactlyOnceWith(1)
      expect(api.getActiveVenueOfferByEan).toHaveBeenCalledExactlyOnceWith(4, 2)

      expect(result.current.hasPublishedOfferWithSameEan).toBe(true)
    })

    it('should check for EAN duplicate and set hasPublishedOfferWithSameEan to false when there is none', async () => {
      vi.spyOn(api, 'getOffer').mockResolvedValueOnce({
        ...offerBase,
        extraData: { ean: 2 },
        productId: 3,
        venue: offerVenueFactory({ id: 4 }),
      })
      vi.spyOn(api, 'getActiveVenueOfferByEan').mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 404 } as ApiResult, '')
      )

      const { result } = await renderUseIndividualOfferContext()

      expect(api.getOffer).toHaveBeenCalledExactlyOnceWith(1)
      expect(api.getActiveVenueOfferByEan).toHaveBeenCalledWith(4, 2)

      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
    })

    it('should both expose isEvent from offer and ignore any setIsEvent override', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isEvent).toBe(false)

      await waitFor(() => void result.current.setIsEvent(true))

      expect(result.current.isEvent).toBe(false)
    })

    it('should allow toggling isAccessibilityFilled via setter', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isAccessibilityFilled).toBe(true)

      await waitFor(() => void result.current.setIsAccessibilityFilled(false))

      expect(result.current.isAccessibilityFilled).toBe(false)
    })
  })
})
