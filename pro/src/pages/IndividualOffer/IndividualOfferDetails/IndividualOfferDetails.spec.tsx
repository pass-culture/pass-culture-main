import { screen } from '@testing-library/react'
import useSWR, { type SWRResponse } from 'swr'
import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import type { GetOffererResponseModel } from '@/apiClient/v1'
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

import { Component as IndividualOfferDetails } from './IndividualOfferDetails'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))
vi.mock('./components/IndividualOfferDetailsScreen', () => ({
  IndividualOfferDetailsScreen: ({ venues }: { venues: unknown[] }) => (
    <div data-testid="details-screen">venues:{venues.length}</div>
  ),
}))

const renderIndividualOfferDetails: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params) => {
  const contextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferDetails />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferDetails />', () => {
  const useSWRMock = vi.mocked(useSWR)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render spinner when venues are loading', () => {
    useSWRMock.mockReturnValue({
      isLoading: true,
    } as SWRResponse)

    const offer = getIndividualOfferFactory({
      venue: makeVenueListItem({
        id: 99,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 7,
          allowedOnAdage: true,
        }),
        managingOffererId: 7,
      }),
    })
    const contextValues = { offer }

    renderIndividualOfferDetails({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()

    expect(useSWRMock).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )
  })

  it('should render IndividualOfferDetails', () => {
    const venuesData = {
      venues: [makeVenueListItem({ id: 2 })],
    }
    useSWRMock.mockImplementation(
      () =>
        ({
          isLoading: false,
          data: venuesData,
        }) as SWRResponse
    )

    const offer = getIndividualOfferFactory()
    const contextValues = { offer }

    renderIndividualOfferDetails({ contextValues })

    expect(screen.getByTestId('details-screen')).toHaveTextContent('venues:1')

    expect(useSWRMock).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )
  })

  it('should use selectedOffererId from redux when offer has no managingOfferer id', async () => {
    useSWRMock.mockImplementation(
      () =>
        ({
          isLoading: false,
          data: { venues: [] },
        }) as SWRResponse
    )

    const offer = getIndividualOfferFactory()
    // We deliberately remove the nested id to test Redux fallback
    // @ts-expect-error Test-specific mutation to simulate missing id.
    delete offer.venue.managingOfferer.id

    const contextValues: IndividualOfferContextValues = {
      ...individualOfferContextValuesFactory(),
      offer,
    }
    const options = {
      storeOverrides: {
        offerer: {
          currentOfferer: {
            id: 1,
          } as GetOffererResponseModel,
        },
      },
    }

    renderIndividualOfferDetails({ contextValues, options })

    expect(useSWRMock).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )

    // When falling back to Redux selected offerer, the fetcher should call the API with that id
    const fetcher = useSWRMock.mock.calls[0][1]

    await fetcher!([GET_VENUES_QUERY_KEY, 1])

    expect(api.getVenues).toHaveBeenCalledWith(null, true, 1)
  })
})
