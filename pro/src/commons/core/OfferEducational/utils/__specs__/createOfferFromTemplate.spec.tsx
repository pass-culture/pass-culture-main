import { act, renderHook } from '@testing-library/react'
import type { PropsWithChildren } from 'react'
import { SWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { useCreateOfferFromTemplate } from '../createOfferFromTemplate'
import { postCollectiveOfferImage } from '../postCollectiveOfferImage'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: vi.fn(async () =>
      getCollectiveOfferTemplateFactory()
    ),
    listEducationalOfferers: vi.fn(async () => ({ educationalOfferers: [] })),
    createCollectiveOffer: vi.fn(async () => ({ id: 2 })),
  },
}))
vi.mock('../computeInitialValuesFromOffer', () => ({
  computeInitialValuesFromOffer: vi.fn(() => ({})),
}))
vi.mock('../createOfferPayload', () => ({
  createCollectiveOfferPayload: vi.fn(() => ({ name: 'Created offer' })),
}))
vi.mock('../postCollectiveOfferImage', () => ({
  postCollectiveOfferImage: vi.fn(),
}))

const wrapper = ({ children }: PropsWithChildren) => (
  <SWRConfig value={{ provider: () => new Map() }}>{children}</SWRConfig>
)

describe('useCreateOfferFromTemplate', () => {
  const navigate = vi.fn()
  const snackBar = { error: vi.fn(), success: vi.fn() }
  const setIsCreatingNewOffer = vi.fn()
  const venue = makeGetVenueResponseModel({ id: 1 })

  it('should fetch and create only when triggered, duplicate the image and navigate', async () => {
    const { result } = renderHook(() => useCreateOfferFromTemplate(), {
      wrapper,
    })

    expect(api.getCollectiveOfferTemplate).not.toHaveBeenCalled()
    expect(api.listEducationalOfferers).not.toHaveBeenCalled()
    expect(api.createCollectiveOffer).not.toHaveBeenCalled()

    await act(async () => {
      await result.current(navigate, snackBar, 1, venue, 'request-id')
    })

    expect(api.getCollectiveOfferTemplate).toHaveBeenCalledWith({
      path: { offer_id: 1 },
    })
    const template = await vi.mocked(api.getCollectiveOfferTemplate).mock
      .results[0].value
    const offererId = template.venue.managingOfferer.id
    expect(api.listEducationalOfferers).toHaveBeenCalledWith({
      query: { offererId },
    })
    expect(api.createCollectiveOffer).toHaveBeenCalledWith({
      body: { name: 'Created offer' },
    })
    expect(postCollectiveOfferImage).toHaveBeenCalledWith({
      initialValues: {},
      snackBar,
      id: 2,
    })
    expect(navigate).toHaveBeenCalledWith(
      `/offre/collectif/2/creation?structure=${offererId}&requete=request-id`
    )
  })

  it.each(['getCollectiveOfferTemplate', 'listEducationalOfferers'] as const)(
    'should report retrieval errors from %s and reset the loading state',
    async (method) => {
      vi.mocked(api[method]).mockRejectedValueOnce(
        new Error('Retrieval failed')
      )
      const { result } = renderHook(() => useCreateOfferFromTemplate(), {
        wrapper,
      })

      await act(async () => {
        await result.current(
          navigate,
          snackBar,
          1,
          venue,
          undefined,
          false,
          setIsCreatingNewOffer
        )
      })

      expect(snackBar.error).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la récupération de votre offre'
      )
      expect(setIsCreatingNewOffer).toHaveBeenCalledWith(false)
      expect(api.createCollectiveOffer).not.toHaveBeenCalled()
      expect(navigate).not.toHaveBeenCalled()
    }
  )

  it('should report creation errors and reset the loading state', async () => {
    vi.mocked(api.createCollectiveOffer).mockRejectedValueOnce(
      new Error('Creation failed')
    )
    const { result } = renderHook(() => useCreateOfferFromTemplate(), {
      wrapper,
    })

    await act(async () => {
      await result.current(
        navigate,
        snackBar,
        1,
        venue,
        undefined,
        false,
        setIsCreatingNewOffer
      )
    })

    expect(snackBar.error).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
    expect(setIsCreatingNewOffer).toHaveBeenCalledWith(false)
    expect(postCollectiveOfferImage).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
