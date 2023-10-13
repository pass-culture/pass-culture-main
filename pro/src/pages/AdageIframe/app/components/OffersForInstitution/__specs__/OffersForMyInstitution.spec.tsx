import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch'

import { AlgoliaQueryContextProvider } from 'pages/AdageIframe/app/providers'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultUseInfiniteHitsReturn,
  defaultUseStatsReturn,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffersForMyInstitution from '../OffersForMyInstitution'

vi.mock('utils/config', async () => {
  return {
    ...((await vi.importActual('utils/config')) ?? {}),
    ALGOLIA_API_KEY: 'adage-api-key',
    ALGOLIA_APP_ID: '1',
    ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
  }
})

vi.mock('react-instantsearch', async () => {
  return {
    ...((await vi.importActual('react-instantsearch')) ?? {}),
    Configure: vi.fn(() => <div />),
    useStats: () => ({
      ...defaultUseStatsReturn,
      nbHits: 2,
    }),
    useInfiniteHits: () => ({
      ...defaultUseInfiniteHitsReturn,
      hits: defaultUseInfiniteHitsReturn.hits,
      results: { queryID: 'queryId' },
    }),
    useInstantSearch: () => ({
      scopedResults: [
        {
          indexId: 'test-props-value',
          results: { ...defaultUseStatsReturn, queryID: 'queryId' },
        },
      ],
    }),
  }
})

const renderOffersForMyInstitution = () => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AlgoliaQueryContextProvider>
        <OffersForMyInstitution />
      </AlgoliaQueryContextProvider>
    </AdageUserContextProvider>
  )
}

describe('OffersInstitutionList', () => {
  it('should display list of offers for my institution', async () => {
    renderOffersForMyInstitution()

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(Configure).toHaveBeenCalledWith(
      {
        attributesToHighlight: [],
        attributesToRetrieve: [
          'objectID',
          'offer.dates',
          'offer.name',
          'offer.thumbUrl',
          'venue.name',
          'venue.publicName',
          'isTemplate',
          'offer.interventionArea',
        ],
        clickAnalytics: true,
        facetFilters: ['offer.educationalInstitutionUAICode:1234567A'],
        hitsPerPage: 8,
        distinct: false,
      },
      {}
    )
  })
})
