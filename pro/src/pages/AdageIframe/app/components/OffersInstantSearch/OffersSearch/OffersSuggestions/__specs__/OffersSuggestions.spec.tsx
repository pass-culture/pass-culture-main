import { screen } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch'
import * as instantSearch from 'react-instantsearch'

import { AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { OfferAddressType } from 'apiClient/v1'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
  defaultUseInfiniteHitsReturn,
  defaultUseStatsReturn,
} from 'utils/adageFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../../utils'
import { OffersSuggestions, OffersSuggestionsProps } from '../OffersSuggestions'

type InstantSearchHookResultMock = {
  scopedResults: {
    indexId: string
    results: {
      hits: typeof defaultUseInfiniteHitsReturn.hits
      nbHits: number
    }
  }[]
}

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOffer: vi.fn(),
  },
}))

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: false,
    addListener: vi.fn(),
    removeListener: vi.fn(),
  }),
})

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
    )
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
          [
            'offer.eventAddressType:offererVenue',
            'offer.eventAddressType:other',
          ],
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
    )
  })

  it('should show the result independently of the intervention type filter when the intervention type filter was set', () => {
    renderOffersSuggestionsComponent(
      {
        formValues: {
          ...props.formValues,
          eventAddressType: OfferAddressType.SCHOOL,
        },
      },
      user
    )

    expect(Configure).toHaveBeenCalledTimes(3)
    expect(Configure).toHaveBeenCalledWith(
      expect.objectContaining({
        aroundRadius: 30_000_000,
        facetFilters: [
          [
            'offer.educationalInstitutionUAICode:all',
            'offer.educationalInstitutionUAICode:1234567A',
          ],
        ],
      }),
      {}
    )
    expect(
      screen.getByText(
        'Découvrez des offres qui relèvent d’autres types d’intervention'
      )
    )
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
        facetFilters: [
          [
            'offer.educationalInstitutionUAICode:all',
            'offer.educationalInstitutionUAICode:1234567A',
          ],
        ],
      }),
      {}
    )
    expect(
      screen.getByText(
        'Découvrez des offres qui relèvent d’autres domaines artistiques'
      )
    )
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
        facetFilters: [
          [
            'offer.educationalInstitutionUAICode:all',
            'offer.educationalInstitutionUAICode:1234567A',
          ],
        ],
      }),
      {}
    )
    expect(
      screen.getByText('Découvrez des offres qui relèvent d’autres formats')
    )
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
