import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'
import { QueryCache, QueryClient, QueryClientProvider } from 'react-query'

import {
  OffersComponent as Offers,
  OffersComponentProps,
} from 'app/components/OffersInstantSearch/OffersSearch/Offers/Offers'
import { AlgoliaQueryContextProvider } from 'app/providers/AlgoliaQueryContextProvider'
import {
  filtersContextInitialValues,
  FiltersContextProvider,
  FiltersContextType,
} from 'app/providers/FiltersContextProvider'
import * as pcapi from 'repository/pcapi/pcapi'
import { ADRESS_TYPE, OfferType, ResultType, Role } from 'utils/types'

jest.mock('repository/pcapi/pcapi', () => ({
  getOffer: jest.fn(),
}))

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    Stats: jest.fn(() => <div>2 résultats</div>),
  }
})

const queryCache = new QueryCache()
const queryClient = new QueryClient({ queryCache })
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

const searchFakeResult: Hit<ResultType> = {
  objectID: '479',
  offer: {
    dates: [new Date('2021-09-29T13:54:30+00:00').valueOf()],
    name: 'Une chouette à la mer',
    thumbUrl: '/storage/thumbs/mediations/AFXA',
  },
  venue: {
    name: 'Le Petit Rintintin 25',
    publicName: 'Le Petit Rintintin 25',
  },
  _highlightResult: {},
}

const renderOffers = (
  props: OffersComponentProps,
  filterContextProviderValue: FiltersContextType = filtersContextInitialValues
) =>
  render(
    <FiltersContextProvider values={filterContextProviderValue}>
      <AlgoliaQueryContextProvider>
        <Offers {...props} />
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>,
    { wrapper }
  )

describe('offer', () => {
  let offerInParis: OfferType
  let offerInCayenne: OfferType
  let offersProps: OffersComponentProps

  beforeEach(() => {
    queryCache.clear()
    offerInParis = {
      id: 479,
      description: 'Une offre vraiment chouette',
      name: 'Une chouette à la mer',
      subcategoryLabel: 'Cinéma',
      stocks: [
        {
          id: 825,
          beginningDatetime: new Date('2022-09-16T00:00:00Z'),
          bookingLimitDatetime: new Date('2022-09-16T00:00:00Z'),
          isBookable: true,
          price: 140000,
          numberOfTickets: 10,
        },
      ],
      venue: {
        address: '1 boulevard Poissonnière',
        city: 'Paris',
        name: 'Le Petit Rintintin 33',
        postalCode: '75000',
        publicName: 'Le Petit Rintintin 33',
        managingOfferer: {
          name: 'Le Petit Rintintin Management',
        },
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
      },
      extraData: {
        offerVenue: {
          venueId: 'VENUE_ID',
          otherAddress: '',
          addressType: ADRESS_TYPE.OFFERER_VENUE,
        },
        students: ['Collège - 4e', 'Collège - 3e'],
      },
      isSoldOut: false,
      isExpired: false,
      audioDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
    }

    offerInCayenne = {
      id: 479,
      description: 'Une offre vraiment chouette',
      name: 'Une chouette à la mer',
      subcategoryLabel: 'Cinéma',
      stocks: [
        {
          id: 825,
          beginningDatetime: new Date('2021-09-25T22:00:00Z'),
          bookingLimitDatetime: new Date('2021-09-25T22:00:00Z'),
          isBookable: true,
          price: 0,
          educationalPriceDetail: 'Le détail de mon prix',
        },
      ],
      venue: {
        address: '1 boulevard Poissonnière',
        city: 'Paris',
        name: 'Le Petit Rintintin 33',
        postalCode: '97300',
        publicName: 'Le Petit Rintintin 33',
        managingOfferer: {
          name: 'Le Petit Rintintin Management',
        },
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
      },
      extraData: {
        offerVenue: {
          venueId: '',
          otherAddress: 'A la mairie',
          addressType: ADRESS_TYPE.OTHER,
        },
        students: ['Collège - 4e'],
      },
      isSoldOut: false,
      isExpired: false,
      audioDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
    }

    offersProps = {
      hits: [searchFakeResult],
      setIsLoading: jest.fn(),
      userRole: Role.redactor,
      handleResetFiltersAndLaunchSearch: jest.fn(),
    }
  })

  describe('offer item', () => {
    it('should not show all information at first', async () => {
      // Given
      mockedPcapi.getOffer.mockResolvedValue(offerInParis)

      // When
      renderOffers(offersProps)

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()
      const listItemsInOffer = screen.getAllByTestId('offer-listitem')
      const summaryList = within(listItemsInOffer[0]).getAllByRole('list')
      expect(summaryList).toHaveLength(2)

      // First summary line
      expect(within(summaryList[0]).getByText('Cinéma')).toBeInTheDocument()
      expect(
        within(summaryList[0]).getByText('16/09/2022 à 02:00')
      ).toBeInTheDocument()
      expect(
        within(summaryList[0]).getByText('75000, Paris')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryList[1]).getByText('Jusqu’à 10 places')
      ).toBeInTheDocument()
      expect(within(summaryList[1]).getByText('1 400,00 €')).toBeInTheDocument()
      expect(
        within(summaryList[1]).getByText('Multi niveaux')
      ).toBeInTheDocument()

      // Info that are in offer details component
      expect(
        screen.queryByText('Moteur', { exact: false })
      ).not.toBeInTheDocument()
    })

    it('should show all offer informations if user click on "en savoir plus"', async () => {
      // Given
      mockedPcapi.getOffer.mockResolvedValue(offerInCayenne)

      // When
      renderOffers(offersProps)

      const offerName = await screen.findByText(offerInCayenne.name)
      expect(offerName).toBeInTheDocument()
      const listItemsInOffer = screen.getAllByTestId('offer-listitem')
      const summaryList = within(listItemsInOffer[0]).getAllByRole('list')
      expect(summaryList).toHaveLength(2)

      // First summary line
      expect(within(summaryList[0]).getByText('Cinéma')).toBeInTheDocument()
      expect(
        within(summaryList[0]).getByText('25/09/2021 à 19:00')
      ).toBeInTheDocument()
      expect(
        within(summaryList[0]).getByText('A la mairie')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryList[1]).queryByText('Jusqu’à', { exact: false })
      ).not.toBeInTheDocument()
      expect(within(summaryList[1]).getByText('Gratuit')).toBeInTheDocument()
      expect(
        within(summaryList[1]).getByText('Collège - 4e')
      ).toBeInTheDocument()

      const seeMoreButton = await screen.findByRole('button', {
        name: 'en savoir plus',
      })
      userEvent.click(seeMoreButton)

      await waitFor(() => {
        expect(screen.queryByText('Le détail de mon prix')).toBeInTheDocument()
      })

      // Info that are in offer details component
      expect(screen.queryByText('Le détail de mon prix')).toBeInTheDocument()
      expect(screen.queryByText('Moteur', { exact: false })).toBeInTheDocument()
      expect(
        screen.queryByText('Psychique ou cognitif', { exact: false })
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Auditif', { exact: false })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Visuel', { exact: false })
      ).not.toBeInTheDocument()
    })
  })
})
