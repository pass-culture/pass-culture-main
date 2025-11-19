import { screen } from '@testing-library/react'
import { vi } from 'vitest'

import { api } from '@/apiClient/api'
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
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferLocation } from './IndividualOfferLocation'

vi.mock('swr', async (importOriginal) => {
  const actual = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    __esModule: true,
    default: vi.fn(), // mocked useSWR
  }
})

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))

// Mock layout subcomponents / heavy children to isolate this component
vi.mock('./components/IndividualOfferLocationScreen', () => ({
  IndividualOfferLocationScreen: ({ venues }: { venues: unknown[] }) => (
    <div data-testid="location-screen">
      Child Screen – venues:{venues.length}
    </div>
  ),
}))

vi.mock('@/components/IndividualOfferLayout/IndividualOfferLayout', () => ({
  IndividualOfferLayout: ({
    children,
    title,
  }: {
    children: React.ReactNode
    title: string
  }) => (
    <div>
      <h1>{title}</h1>
      <div data-testid="layout-child">{children}</div>
    </div>
  ),
}))

// We import after mock so the default export is already mocked
import useSWR from 'swr'

import { makeGetVenueManagingOffererResponseModel } from '@/commons/utils/factories/venueFactories'

const mockUseSWR = useSWR as unknown as {
  mockReturnValue: (v: unknown) => void
  mockImplementation: (fn: () => unknown) => void
}

describe('<IndividualOfferLocation />', () => {
  const renderComponent = (
    contextOverride?: Partial<IndividualOfferContextValues>
  ) => {
    const contextValue: IndividualOfferContextValues = {
      ...individualOfferContextValuesFactory(),
      ...contextOverride,
    }

    return renderWithProviders(
      <IndividualOfferContext.Provider value={contextValue}>
        <IndividualOfferLocation />
      </IndividualOfferContext.Provider>,
      {
        user: sharedCurrentUserFactory(),
      }
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders spinner when no offer in context', () => {
    // No offer => early return branch
    mockUseSWR.mockReturnValue({ isLoading: false })
    renderComponent({
      offer: undefined as unknown as IndividualOfferContextValues['offer'],
    })
    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('renders spinner when venues are loading', () => {
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
    mockUseSWR.mockReturnValue({ isLoading: true })
    renderComponent({ offer })
    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('calls api.getVenues with managingOfferer id and renders child screen with venues', async () => {
    const offer = getIndividualOfferFactory({
      venue: makeVenueListItem({
        id: 5,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 42,
          allowedOnAdage: true,
        }),
        managingOffererId: 42,
      }),
    })
    const venuesData = {
      venues: [makeVenueListItem({ id: 1 }), makeVenueListItem({ id: 2 })],
    }
    mockUseSWR.mockImplementation(() => ({
      isLoading: false,
      data: venuesData,
    }))

    ;(
      api.getVenues as unknown as { mockResolvedValue: (d: unknown) => void }
    ).mockResolvedValue(venuesData)

    renderComponent({ offer })

    expect(mockUseSWR).toHaveBeenCalledWith(
      [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id],
      expect.any(Function),
      { fallbackData: { venues: [] } }
    )

    expect(screen.getByTestId('location-screen')).toHaveTextContent('venues:2')

    // Execute fetcher manually to cover fetcher line
    const fetcher = (mockUseSWR as unknown as { mock: { calls: unknown[][] } })
      .mock.calls[0][1] as (args: [string, number]) => Promise<unknown>
    await fetcher([GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id])
    expect(api.getVenues).toHaveBeenCalledWith(null, true, 42)
  })
})
