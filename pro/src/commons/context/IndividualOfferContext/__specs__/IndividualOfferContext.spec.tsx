import { screen, waitFor } from '@testing-library/react'

import { ApiError } from 'apiClient/adage'
import { ApiRequestOptions } from 'apiClient/adage/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/adage/core/ApiResult'
import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { IndividualOfferContextProvider } from '../IndividualOfferContext'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useLocation: vi.fn(),
  useParams: () => ({
    offerId: '1',
  }),
}))

const apiOffer: GetIndividualOfferWithAddressResponseModel =
  getIndividualOfferFactory()

const renderIndividualOfferContextProvider = () =>
  renderWithProviders(
    <IndividualOfferContextProvider>
      Test inner content
    </IndividualOfferContextProvider>
  )

describe('IndividualOfferContextProvider', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  })

  it('should initialize context with api', async () => {
    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(api.getCategories).toHaveBeenCalled()
    })
  })

  it('should check if there is another offer on the venue with the same EAN', async () => {
    vi.spyOn(api, 'getOffer').mockResolvedValueOnce({
      ...apiOffer,
      productId: 1,
      extraData: { ean: 2 },
    })

    const spy = vi
      .spyOn(api, 'getActiveVenueOfferByEan')
      .mockResolvedValueOnce({
        id: 1,
        dateCreated: '',
        isActive: true,
        name: 'test',
        status: OfferStatus.ACTIVE,
        subcategoryId: SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_CD,
      })

    renderIndividualOfferContextProvider()

    await waitFor(() => {
      expect(spy).toHaveBeenCalledOnce()
    })
  })

  it('should consider that there is no other offer with the same ean if the api responds with a 404 error', async () => {
    vi.spyOn(api, 'getOffer').mockResolvedValueOnce({
      ...apiOffer,
      productId: 1,
      extraData: { ean: 2 },
    })

    vi.spyOn(api, 'getActiveVenueOfferByEan').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 404,
        } as ApiResult,
        ''
      )
    )

    renderIndividualOfferContextProvider()

    expect(await screen.findByText('Test inner content')).toBeInTheDocument()
  })
})
