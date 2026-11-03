import { act, renderHook } from '@testing-library/react'
import type { PropsWithChildren } from 'react'
import { SWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { useDuplicateBookableOffer } from '../duplicateBookableOffer'
import { postCollectiveOfferImage } from '../postCollectiveOfferImage'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(async () => getCollectiveOfferFactory()),
    listEducationalOfferers: vi.fn(async () => ({ educationalOfferers: [] })),
    duplicateCollectiveOffer: vi.fn(async () => ({ id: 2 })),
  },
}))
vi.mock('../computeInitialValuesFromOffer', () => ({
  computeInitialValuesFromOffer: vi.fn(() => ({})),
}))
vi.mock('../postCollectiveOfferImage', () => ({
  postCollectiveOfferImage: vi.fn(),
}))

const wrapper = ({ children }: PropsWithChildren) => (
  <SWRConfig value={{ provider: () => new Map() }}>{children}</SWRConfig>
)

describe('useDuplicateBookableOffer', () => {
  const navigate = vi.fn()
  const snackBar = { error: vi.fn(), success: vi.fn() }
  const venue = makeGetVenueResponseModel({ id: 1 })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should fetch and duplicate only when triggered, attach the image and navigate', async () => {
    const { result } = renderHook(() => useDuplicateBookableOffer(), {
      wrapper,
    })

    expect(api.getCollectiveOffer).not.toHaveBeenCalled()
    expect(api.listEducationalOfferers).not.toHaveBeenCalled()
    expect(api.duplicateCollectiveOffer).not.toHaveBeenCalled()

    await act(async () => {
      await result.current(navigate, snackBar, 1, venue)
    })

    expect(api.getCollectiveOffer).toHaveBeenCalledWith({
      path: { offer_id: 1 },
    })
    const offer = await vi.mocked(api.getCollectiveOffer).mock.results[0].value
    const offererId = offer.venue.managingOfferer.id
    expect(api.listEducationalOfferers).toHaveBeenCalledWith({
      query: { offererId },
    })
    expect(api.duplicateCollectiveOffer).toHaveBeenCalledWith({
      path: { offer_id: 1 },
    })
    expect(postCollectiveOfferImage).toHaveBeenCalledWith({
      initialValues: {},
      snackBar,
      id: 2,
    })
    expect(navigate).toHaveBeenCalledWith(
      `/offre/collectif/2/creation?structure=${offererId}`
    )
  })

  it('should report retrieval errors without attempting duplication', async () => {
    vi.mocked(api.getCollectiveOffer).mockRejectedValueOnce(
      new Error('Retrieval failed')
    )
    const { result } = renderHook(() => useDuplicateBookableOffer(), {
      wrapper,
    })

    await act(async () => {
      await result.current(navigate, snackBar, 1, venue)
    })

    expect(snackBar.error).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
    expect(api.duplicateCollectiveOffer).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })

  it('should report duplication errors', async () => {
    vi.mocked(api.duplicateCollectiveOffer).mockRejectedValueOnce(
      new Error('Duplication failed')
    )
    const { result } = renderHook(() => useDuplicateBookableOffer(), {
      wrapper,
    })

    await act(async () => {
      await result.current(navigate, snackBar, 1, venue)
    })

    expect(snackBar.error).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la création de votre offre'
    )
    expect(postCollectiveOfferImage).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
