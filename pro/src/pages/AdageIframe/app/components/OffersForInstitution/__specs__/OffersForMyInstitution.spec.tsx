import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch'

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

const renderOffersForMyInstitution = (user = defaultAdageUser) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <OffersForMyInstitution />
    </AdageUserContextProvider>
  )
}

describe('OffersInstitutionList', () => {
  it('should display no result page', () => {
    renderOffersForMyInstitution({ ...defaultAdageUser, offersCount: 0 })

    expect(
      screen.getByText('Vous n’avez pas d’offre à préréserver')
    ).toBeInTheDocument()
  })
  it('should display list of offers for my institution', async () => {
    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

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

  it('should display title and banner', async () => {
    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Pour mon établissement'))
    expect(
      screen.getByRole('link', {
        name: /Voir la page “Suivi pass Culture”/i,
      })
    ).toHaveAttribute('href', 'adage/passculture/index')
  })
})
