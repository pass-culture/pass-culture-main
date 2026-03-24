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

import { Component as IndividualOfferDescription } from './IndividualOfferDescription'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))
vi.mock('./components/IndividualOfferDescriptionScreen', async () => {
  const { useState } = await import('react')
  const { useIndividualOfferContext } = await import(
    '@/commons/context/IndividualOfferContext/IndividualOfferContext'
  )

  return {
    IndividualOfferDescriptionScreen: ({ venues }: { venues: unknown[] }) => {
      const { offer } = useIndividualOfferContext()
      const [initialOfferName] = useState(() => offer?.name ?? '')

      return (
        <section>
          <h1>{initialOfferName || 'Nouvelle offre'}</h1>
          <p>venues:{venues.length}</p>
        </section>
      )
    },
  }
})

const renderIndividualOfferDescription: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params) => {
  const contextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...params.contextValues,
  }
  const user = sharedCurrentUserFactory()
  const options: RenderWithProvidersOptions = {
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: makeVenueListItem({ id: 2 }),
      },
    },
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferDescription />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferDescription />', () => {
  const useSWRMock = vi.mocked(useSWR)

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

    renderIndividualOfferDescription({ contextValues })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()

    expect(useSWRMock).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )
  })

  it('should render IndividualOfferDescription', () => {
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

    renderIndividualOfferDescription({ contextValues })

    expect(screen.getByText('venues:1')).toBeInTheDocument()

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
        user: {
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
      },
      offerer: {
        currentOfferer: {
          id: 1,
        } as GetOffererResponseModel,
      },
    }

    renderIndividualOfferDescription({ contextValues, options })

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
