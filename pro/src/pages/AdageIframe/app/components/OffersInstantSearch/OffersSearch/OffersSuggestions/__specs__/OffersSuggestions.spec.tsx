import { screen } from '@testing-library/react'
import * as instantSearch from 'react-instantsearch'
import { Configure } from 'react-instantsearch'

import {
  type AuthenticatedResponse,
  CollectiveLocationType,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
  defaultUseInfiniteHitsReturn,
  defaultUseStatsReturn,
} from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../../utils'
import {
  OffersSuggestions,
  type OffersSuggestionsProps,
} from '../OffersSuggestions'

type InstantSearchHookResultMock = {
  scopedResults: {
    indexId: string
    results: {
      hits: typeof defaultUseInfiniteHitsReturn.hits
      nbHits: number
    }
  }[]
}

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOffer: vi.fn(),
    logOfferListViewSwitch: vi.fn(),
  },
}))

const renderOffersSuggestionsComponent = (
  props: OffersSuggestionsProps,
  user: AuthenticatedResponse,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <OffersSuggestions {...props} />
    </AdageUserContextProvider>,
    options
  )
}

vi.mock('react-instantsearch', async () => {
  return {
    ...(await vi.importActual('react-instantsearch')),
    useInstantSearch: () => ({
      scopedResults: [
        {
          indexId: 'no_results_offers_index_0',
          results: { ...defaultUseInfiniteHitsReturn, nbHits: 1 },
        },
      ],
    }),
    Configure: vi.fn(() => <div />),
    Index: vi.fn(({ children }) => children),
    useStats: () => ({
      ...defaultUseStatsReturn,
      nbHits: 1,
    }),
    useInfiniteHits: () => ({
      ...defaultUseInfiniteHitsReturn,
    }),
    usePagination: () => ({
      currentRefinement: 0,
      nbPages: 3,
      refine: () => {},
    }),
  }
})

describe('OffersSuggestions', () => {
  beforeEach(() => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplate').mockResolvedValue(
      defaultCollectiveTemplateOffer
    )

    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValue(
      defaultCollectiveOffer
    )
  })

  const props: OffersSuggestionsProps = {
    formValues: ADAGE_FILTERS_DEFAULT_VALUES,
  }
  const user = {
    ...defaultAdageUser,
    lat: 10,
    lon: 10,
  }

  it('should show the suggestions header when there are results', () => {
    renderOffersSuggestionsComponent(props, user)

    expect(screen.getByTestId('suggestions-header')).toBeInTheDocument()
  })

  it('should show the nearby (< 5km) offers when no results in initial search with no filters', () => {
    renderOffersSuggestionsComponent(props, user)

    expect(Configure).toHaveBeenCalledTimes(2)
    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        aroundRadius: 5000,
      }),
      {}
    )
    expect(
      screen.getByText(
        'Découvrez des propositions de sorties scolaires à proximité de votre établissement'
      )
    ).toBeInTheDocument()
  })

  it('should show the nearby (< 100km) offers of cultural partners coming to the institution when no results in initial search with no filters', () => {
    vi.spyOn(
      instantSearch as {
        useInstantSearch: () => InstantSearchHookResultMock
      },
      'useInstantSearch'
    ).mockImplementationOnce(() => ({
      scopedResults: [
        {
          indexId: 'no_results_offers_index_0',
          results: {
            hits: [],
            nbHits: 0,
          },
        },
        {
          indexId: 'no_results_offers_index_1',
          results: {
            hits: defaultUseInfiniteHitsReturn.hits,
            nbHits: 1,
          },
        },
      ],
    }))

    renderOffersSuggestionsComponent(props, user)

    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        facetFilters: expect.arrayContaining([
          ['offer.locationType:ADDRESS', 'offer.locationType:TO_BE_DEFINED'],
        ]),
        aroundRadius: 100000,
      }),
      {}
    )
    expect(Configure).toHaveBeenCalledTimes(2)
    expect(
      screen.getByText(
        'Découvrez les offres de partenaires culturels locaux prêts à intervenir dans votre classe'
      )
    ).toBeInTheDocument()
  })

  it('should show the result independently of the intervention type filter when the intervention type filter was set', () => {
    renderOffersSuggestionsComponent(
      {
        formValues: {
          ...props.formValues,
          locationType: CollectiveLocationType.SCHOOL,
        },
      },
      user
    )

    expect(Configure).toHaveBeenCalledTimes(3)
    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        aroundRadius: 30_000_000,
        facetFilters: [],
      }),
      {}
    )
    expect(
      screen.getByText(
        'Découvrez des offres qui relèvent d’autres types d’intervention'
      )
    ).toBeInTheDocument()
  })

  it('should show the result independently of domains filter when the domains filter was set', () => {
    renderOffersSuggestionsComponent(
      {
        formValues: {
          ...props.formValues,
          domains: [2],
        },
      },
      user
    )

    expect(Configure).toHaveBeenCalledTimes(3)
    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        aroundRadius: 30_000_000,
        facetFilters: [],
      }),
      {}
    )
    expect(
      screen.getByText(
        'Découvrez des offres qui relèvent d’autres domaines artistiques'
      )
    ).toBeInTheDocument()
  })

  it('should show the result independently of formats filter when the format filter was set', () => {
    renderOffersSuggestionsComponent(
      {
        formValues: {
          ...props.formValues,
          formats: ['Atelier de pratique'],
        },
      },
      user
    )

    expect(Configure).toHaveBeenCalledTimes(3)
    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        aroundRadius: 30_000_000,
        facetFilters: [],
      }),
      {}
    )
    expect(
      screen.getByText('Découvrez des offres qui relèvent d’autres formats')
    ).toBeInTheDocument()
  })

  it('should not show suggestions header if no offer could be suggested', () => {
    vi.spyOn(
      instantSearch as {
        useInstantSearch: () => InstantSearchHookResultMock
      },
      'useInstantSearch'
    ).mockImplementationOnce(() => ({
      scopedResults: [],
    }))

    renderOffersSuggestionsComponent(props, user)
    expect(
      screen.queryByText(
        'Découvrez des offres qui relèvent d’autres catégories'
      )
    ).not.toBeInTheDocument()
  })
})
