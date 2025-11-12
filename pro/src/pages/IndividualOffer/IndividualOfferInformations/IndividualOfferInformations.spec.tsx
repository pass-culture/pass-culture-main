import { screen } from '@testing-library/react'
import useSWR, { type SWRResponse } from 'swr'
import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueManagingOffererResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferInformations } from './IndividualOfferInformations'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))
vi.mock('./components/IndividualOfferInformationsScreen', () => ({
  IndividualOfferInformationsScreen: () => (
    <div data-testid="informations-screen">
      Individual Offer Information Screen
    </div>
  ),
}))
vi.mock('../IndividualOfferLocation/IndividualOfferLocation', () => ({
  IndividualOfferLocation: () => (
    <div data-testid="location-page">Individual Offer Location Page</div>
  ),
}))

const renderIndividualOfferInformations: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params) => {
  const contextValues: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory({}),
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferInformations />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferInformations />', () => {
  const useSWRMock = vi.mocked(useSWR)

  it('should render spinner when no offer in context', () => {
    useSWRMock.mockReturnValue({
      isLoading: false,
      data: { venues: [] },
    } as SWRResponse)

    const contextValues = { offer: null }

    renderIndividualOfferInformations({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('should render spinner when venues are loading', () => {
    useSWRMock.mockReturnValue({
      isLoading: true,
      data: { venues: [] },
    } as SWRResponse)

    const contextValues = { offer: getIndividualOfferFactory() }

    renderIndividualOfferInformations({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('should render IndividualOfferLocation when FF is active', () => {
    const venuesData = {
      venues: [makeVenueListItem({ id: 4 })],
    }
    useSWRMock.mockImplementation(
      () =>
        ({
          isLoading: false,
          data: venuesData,
        }) as SWRResponse
    )

    const offer = getIndividualOfferFactory({
      venue: makeVenueListItem({
        id: 4,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 42,
          allowedOnAdage: true,
        }),
        managingOffererId: 42,
      }),
    })
    const contextValues = { offer }
    const options = {
      features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'],
    }

    renderIndividualOfferInformations({ contextValues, options })

    expect(screen.getByTestId('location-page')).toBeInTheDocument()
  })

  it('should call api.getVenues and render child screen', async () => {
    const venues = [makeVenueListItem({ id: 4 })]
    useSWRMock.mockImplementation(
      () =>
        ({
          isLoading: false,
          data: { venues },
        }) as SWRResponse
    )

    const offer = getIndividualOfferFactory({
      venue: makeVenueListItem({
        id: 4,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 42,
          allowedOnAdage: true,
        }),
        managingOffererId: 42,
      }),
    })
    const contextValues = { offer }

    renderIndividualOfferInformations({ contextValues })

    expect(useSWRMock).toHaveBeenCalledWith(
      [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id],
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )

    expect(screen.getByTestId('informations-screen')).toBeInTheDocument()

    // Ensure the SWR fetcher delegates to `api.getVenues` with the computed managingOfferer id
    const fetcher = useSWRMock.mock.calls[0][1]

    await fetcher!([GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id])

    expect(api.getVenues).toHaveBeenCalledWith(null, true, 42)
  })

  it('should not call SWR if no offer', () => {
    const venues: VenueListItemResponseModel[] = []
    useSWRMock.mockReturnValue({
      isLoading: false,
      data: { venues },
    } as SWRResponse)

    const contextValues = { offer: null }

    renderIndividualOfferInformations({ contextValues })

    expect(useSWRMock).toHaveBeenCalledWith(null, expect.any(Function), {
      fallbackData: { venues: [] },
    })
  })
})
