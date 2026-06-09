import { act, renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { useParams } from 'react-router'
import { SWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  getIndividualOfferFactory,
  getOfferVenueFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
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
  const store = configureTestStore({
    user: {
      selectedPartnerVenue: makeGetVenueResponseModel({ id: 4 }),
    },
  })

  const wrapper = ({ children }: { children: ReactNode }) => (
    <Provider store={store}>
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
    </Provider>
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
    vi.spyOn(apiNew, 'getActiveVenueOfferByEan')
    vi.spyOn(apiNew, 'getCategories').mockResolvedValue({
      categories: MOCKED_CATEGORIES,
      subcategories: MOCKED_SUBCATEGORIES,
    })
    vi.spyOn(apiNew, 'getOffer')
  })

  describe.each([
    ['when there is no offerId in the URL path', {}],
    ['when offerId = "creation" in the URL path', { offerId: 'creation' }],
  ])('%s', (_, pathParams) => {
    beforeEach(() => {
      vi.mocked(useParams).mockReturnValue(pathParams)
    })

    it('should call the expected api endpoints and return the expected context values', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(apiNew.getOffer).not.toHaveBeenCalled()
      expect(apiNew.getCategories).toHaveBeenCalledOnce()
      expect(apiNew.getActiveVenueOfferByEan).not.toHaveBeenCalled()

      expect(result.current.categories.length).toBeGreaterThan(0)
      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
      expect(result.current.isEvent).toBeNull()
      expect(result.current.offer).toBeNull()
      expect(result.current.offerId).toBeNull()
      expect(result.current.subCategories.length).toBeGreaterThan(0)
    })

    it('should control isControlledEvent via setIsControlledEvent', async () => {
      vi.mocked(useParams).mockReturnValue({
        offerId: 'creation',
      } as unknown as ReturnType<typeof useParams>)

      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isEvent).toBeNull()
      expect(result.current.offerId).toBeNull()

      act(() => result.current.setIsControlledEvent(true))

      expect(result.current.isEvent).toBe(true)
      expect(result.current.offerId).toBeNull()
    })
  })

  describe('when there is an offerId in the URL', () => {
    beforeEach(() => {
      vi.mocked(useParams).mockReturnValue({
        offerId: '1',
      })
      vi.spyOn(apiNew, 'getOffer').mockResolvedValue(offerBase)
    })

    it('should call the expected api endpoints and return the expected context values', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(apiNew.getOffer).toHaveBeenCalledExactlyOnceWith({
        path: { offer_id: 1 },
      })
      expect(apiNew.getCategories).toHaveBeenCalledOnce()
      expect(apiNew.getActiveVenueOfferByEan).not.toHaveBeenCalled() // because `offerBase` doesn't meet EAN check criteria

      expect(result.current.categories.length).toBeGreaterThan(0)
      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
      expect(result.current.isEvent).toBe(false)
      expect(result.current.offer?.id).toBe(1)
      expect(result.current.offerId).toBe(1)
      expect(result.current.subCategories.length).toBeGreaterThan(0)
    })

    it('should redirect to an error page when the offer does not exist', async () => {
      vi.spyOn(apiNew, 'getOffer').mockRejectedValueOnce({
        status: 404,
      })

      await renderUseIndividualOfferContext()

      expect(mockNavigate).toHaveBeenLastCalledWith('/404', {
        state: { from: 'offer' },
      })
    })

    it('should check for EAN duplicate and set hasPublishedOfferWithSameEan to true when there is one', async () => {
      vi.spyOn(apiNew, 'getOffer').mockResolvedValueOnce({
        ...offerBase,
        extraData: { ean: 2 },
        productId: 3,
        venue: getOfferVenueFactory({ id: 4 }),
      })
      vi.spyOn(apiNew, 'getActiveVenueOfferByEan').mockResolvedValueOnce({
        ...offerBase,
        id: 5,
      })

      const { result } = await renderUseIndividualOfferContext()

      expect(apiNew.getOffer).toHaveBeenCalledExactlyOnceWith({
        path: { offer_id: 1 },
      })
      expect(apiNew.getActiveVenueOfferByEan).toHaveBeenCalledExactlyOnceWith({
        path: { venue_id: 4, ean: 2 },
      })

      expect(result.current.hasPublishedOfferWithSameEan).toBe(true)
    })

    it('should check for EAN duplicate and set hasPublishedOfferWithSameEan to false when there is none', async () => {
      vi.spyOn(apiNew, 'getOffer').mockResolvedValueOnce({
        ...offerBase,
        extraData: { ean: 2 },
        productId: 3,
        venue: getOfferVenueFactory({ id: 4 }),
      })
      vi.spyOn(apiNew, 'getActiveVenueOfferByEan').mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 404 } as ApiResult, '')
      )

      const { result } = await renderUseIndividualOfferContext()

      expect(apiNew.getOffer).toHaveBeenCalledExactlyOnceWith({
        path: { offer_id: 1 },
      })
      expect(apiNew.getActiveVenueOfferByEan).toHaveBeenCalledWith({
        path: { venue_id: 4, ean: 2 },
      })

      expect(result.current.hasPublishedOfferWithSameEan).toBe(false)
    })

    it('should both expose isEvent from offer and ignore any setIsControlledEvent override', async () => {
      const { result } = await renderUseIndividualOfferContext()

      expect(result.current.isEvent).toBe(false)

      act(() => result.current.setIsControlledEvent(true))

      expect(result.current.isEvent).toBe(false)
    })
  })
})
