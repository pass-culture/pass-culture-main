import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'
import { QueryCache, QueryClient, QueryClientProvider } from 'react-query'

import {} from 'app/__spec__/__test_utils__/elements'
import {
  OffersComponent as Offers,
  OffersComponentProps,
} from 'app/components/OffersInstantSearch/OffersSearch/Offers/Offers'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
} from 'app/providers'
import * as pcapi from 'repository/pcapi/pcapi'
import { OfferType, ResultType, Role } from 'utils/types'

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

const searchFakeResults: Hit<ResultType>[] = [
  {
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
  },
  {
    objectID: '480',
    offer: {
      dates: [new Date('2021-09-29T13:54:30+00:00').valueOf()],
      name: 'Coco channel',
      thumbUrl: '',
    },
    venue: {
      name: 'Le Petit Coco',
      publicName: 'Le Petit Coco',
    },
    _highlightResult: {},
  },
]

const renderOffers = (props: OffersComponentProps) => {
  return render(
    <AlgoliaQueryContextProvider>
      <FacetFiltersContextProvider>
        <Offers {...props} />
      </FacetFiltersContextProvider>
    </AlgoliaQueryContextProvider>,
    {
      wrapper,
    }
  )
}

describe('offers', () => {
  let offerInParis: OfferType
  let offerInCayenne: OfferType
  let otherOffer: OfferType
  let offersProps: OffersComponentProps

  beforeEach(() => {
    queryCache.clear()
    offerInParis = {
      id: 479,
      name: 'Une chouette à la mer',
      description: 'Une offre vraiment chouette',
      subcategoryLabel: 'Cinéma',
      stocks: [
        {
          id: 825,
          beginningDatetime: new Date('2022-09-16T00:00:00Z'),
          bookingLimitDatetime: new Date('2022-09-16T00:00:00Z'),
          isBookable: true,
          price: 140000,
        },
      ],
      venue: {
        address: '1 boulevard Poissonnière',
        city: 'Paris',
        name: 'Le Petit Rintintin 33',
        postalCode: '75000',
        publicName: 'Le Petit Rintintin 33',
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
        managingOfferer: {
          name: 'Le Petit Rintintin Management',
        },
      },
      isSoldOut: false,
      isExpired: false,
      visualDisabilityCompliant: true,
      mentalDisabilityCompliant: true,
      audioDisabilityCompliant: true,
      motorDisabilityCompliant: true,
    }

    offerInCayenne = {
      id: 480,
      description: 'Une offre vraiment coco',
      name: 'Coco channel',
      subcategoryLabel: 'Cinéma',
      stocks: [
        {
          id: 826,
          beginningDatetime: new Date('2021-09-25T22:00:00Z'),
          bookingLimitDatetime: new Date('2021-09-25T22:00:00Z'),
          isBookable: true,
          price: 80000,
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
      isSoldOut: false,
      isExpired: false,
      visualDisabilityCompliant: true,
      mentalDisabilityCompliant: true,
      audioDisabilityCompliant: true,
      motorDisabilityCompliant: true,
    }

    otherOffer = {
      id: 481,
      description: 'Une autre offre',
      name: 'Un autre titre',
      subcategoryLabel: 'Cinéma',
      stocks: [
        {
          id: 827,
          beginningDatetime: new Date('2021-09-25T22:00:00Z'),
          bookingLimitDatetime: new Date('2021-09-25T22:00:00Z'),
          isBookable: true,
          price: 3000,
        },
      ],
      venue: {
        address: '1 boulevard Poissonnière',
        city: 'Paris',
        name: 'Un autre lieu',
        postalCode: '97300',
        publicName: 'Le Petit Rintintin 33',
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
        managingOfferer: {
          name: 'Le Petit Rintintin Management',
        },
      },
      isSoldOut: false,
      isExpired: false,
      visualDisabilityCompliant: true,
      mentalDisabilityCompliant: true,
      audioDisabilityCompliant: true,
      motorDisabilityCompliant: true,
    }

    offersProps = {
      handleResetFiltersAndLaunchSearch: jest.fn(),
      hits: searchFakeResults,
      setIsLoading: jest.fn(),
      userRole: Role.redactor,
    }
  })

  it('should display two offers with their respective stocks when two bookable offers', async () => {
    // Given
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInParis)
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)

    // When
    renderOffers(offersProps)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)
    expect(screen.getByText(offerInParis.name)).toBeInTheDocument()
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
    expect(screen.getByText('2 résultats')).toBeInTheDocument()
  })

  it('should remove previous rendered offers on results update', async () => {
    // Given
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInParis)
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)
    const { rerender } = renderOffers(offersProps)
    mockedPcapi.getOffer.mockResolvedValueOnce(otherOffer)
    const otherSearchResult: Hit<ResultType> = {
      objectID: '481',
      offer: {
        dates: [new Date('2021-09-29T13:54:30+00:00').valueOf()],
        name: 'Un autre titre',
        thumbUrl: '',
      },
      venue: {
        name: 'Un autre lieu',
        publicName: 'Un autre lieu public',
      },
      _highlightResult: {},
    }

    // When
    offersProps.hits = [otherSearchResult]
    rerender(<Offers {...offersProps} />)

    // Then
    const otherOfferName = await screen.findByText(otherOffer.name)
    expect(otherOfferName).toBeInTheDocument()
    expect(screen.getAllByTestId('offer-listitem')).toHaveLength(1)
    expect(screen.queryByText(offerInParis.name)).not.toBeInTheDocument()
    expect(screen.queryByText(offerInCayenne.name)).not.toBeInTheDocument()
    expect(screen.getByText('2 résultats')).toBeInTheDocument()
  })

  it('should show most recent results and cancel previous request', async () => {
    // Given
    mockedPcapi.getOffer.mockReturnValueOnce(
      new Promise(resolve => setTimeout(() => resolve(offerInParis), 500))
    )
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)
    const { rerender } = renderOffers(offersProps)
    mockedPcapi.getOffer.mockResolvedValueOnce(otherOffer)
    const otherSearchResult: Hit<ResultType> = {
      objectID: '481',
      offer: {
        dates: [new Date('2021-09-29T13:54:30+00:00').valueOf()],
        name: 'Un autre titre',
        thumbUrl: '',
      },
      venue: {
        name: 'Un autre lieu',
        publicName: 'Un autre lieu public',
      },
      _highlightResult: {},
    }

    // When
    offersProps.hits = [otherSearchResult]
    rerender(<Offers {...offersProps} />)

    // Then
    const otherOfferName = await screen.findByText(otherOffer.name)
    expect(otherOfferName).toBeInTheDocument()
    expect(screen.getAllByTestId('offer-listitem')).toHaveLength(1)

    await expect(async () => {
      await waitFor(() =>
        expect(screen.getByText(offerInParis.name)).toBeInTheDocument()
      )
    }).rejects.toStrictEqual(expect.anything())
  })

  it('should show a loader while waiting for response', async () => {
    // Given
    mockedPcapi.getOffer.mockReturnValueOnce(
      new Promise(resolve => setTimeout(() => resolve(offerInParis), 500))
    )
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)

    // When
    renderOffers(offersProps)

    // Then
    const loader = await screen.findByText('Recherche en cours')
    expect(loader).toBeInTheDocument()
    const offerInParisName = await screen.findByText(offerInParis.name)
    expect(offerInParisName).toBeInTheDocument()
  })

  it('should display only non sold-out offers', async () => {
    // Given
    offerInParis.isSoldOut = true
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInParis)
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)

    // When
    renderOffers(offersProps)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  it('should not display expired offer', async () => {
    // Given
    offerInParis.isExpired = true
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInParis)
    mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)

    // When
    renderOffers(offersProps)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  describe('should display no results page', () => {
    it('when there are no results', async () => {
      // When
      offersProps.hits = []
      renderOffers(offersProps)

      // Then
      const errorMessage = await screen.findByText(
        'Aucun résultat trouvé pour cette recherche.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })

    it('when all offers are not bookable', async () => {
      // Given
      offerInParis.isExpired = true
      offerInCayenne.isSoldOut = true
      mockedPcapi.getOffer.mockResolvedValueOnce(offerInParis)
      mockedPcapi.getOffer.mockResolvedValueOnce(offerInCayenne)

      // When
      renderOffers(offersProps)

      // Then
      const errorMessage = await screen.findByText(
        'Aucun résultat trouvé pour cette recherche.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })

    it('when offers are not found', async () => {
      // Given
      mockedPcapi.getOffer.mockRejectedValue('Offre inconnue')
      mockedPcapi.getOffer.mockRejectedValue('Offre inconnue')

      // When
      renderOffers(offersProps)

      // Then
      const errorMessage = await screen.findByText(
        'Aucun résultat trouvé pour cette recherche.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })
  })
})
