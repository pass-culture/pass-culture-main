import React from 'react'
import { Configure } from 'react-instantsearch-dom'

import { AlgoliaQueryContextProvider } from 'pages/AdageIframe/app/providers'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
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

vi.mock('../../OffersInstantSearch/OffersSearch/Offers/Offers', () => {
  return {
    Offers: vi.fn(() => <div />),
  }
})

vi.mock('react-instantsearch-dom', async () => {
  return {
    ...((await vi.importActual('react-instantsearch-dom')) ?? {}),
    Configure: vi.fn(() => <div />),
    connectStats: vi.fn(Component => (props: any) => (
      <Component
        {...props}
        areHitsSorted={false}
        nbHits={0}
        nbSortedHits={0}
        processingTimeMS={0}
        hits={[]}
      />
    )),
  }
})

const renderOffersForMyInstitution = () => {
  renderWithProviders(
    <AdageUserContext.Provider value={{ adageUser: defaultAdageUser }}>
      <AlgoliaQueryContextProvider>
        <OffersForMyInstitution
          removeVenueFilter={() => {}}
          venueFilter={null}
        />
      </AlgoliaQueryContextProvider>
    </AdageUserContext.Provider>
  )
}

describe('OffersInstitutionList', () => {
  it('should display list of offers for my institution', () => {
    renderOffersForMyInstitution()

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
      },
      {}
    )
  })
})
