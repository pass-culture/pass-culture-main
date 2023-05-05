import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'

import {
  AdageFrontRoles,
  CancelablePromise,
  CollectiveOfferResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import {
  AlgoliaQueryContextProvider,
  FacetFiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { renderWithProviders } from 'utils/renderWithProviders'
import { ResultType } from 'utils/types'

import { OffersComponent, OffersComponentProps } from '../Offers'

jest.mock('apiClient/api', () => ({
  apiAdage: { getCollectiveOffer: jest.fn(), logSearchButtonClick: jest.fn() },
}))

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
    isTemplate: false,
    __queryID: 'queryId',
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
    isTemplate: false,
    __queryID: 'queryId',
  },
]

const renderOffers = (props: OffersComponentProps) => {
  return renderWithProviders(
    <AlgoliaQueryContextProvider>
      <FacetFiltersContextProvider>
        <OffersComponent {...props} />
      </FacetFiltersContextProvider>
    </AlgoliaQueryContextProvider>
  )
}

describe('offers', () => {
  let offerInParis: CollectiveOfferResponseModel
  let offerInCayenne: CollectiveOfferResponseModel
  let otherOffer: CollectiveOfferResponseModel
  let offersProps: OffersComponentProps

  beforeEach(() => {
    offerInParis = {
      id: 479,
      name: 'Une chouette à la mer',
      description: 'Une offre vraiment chouette',
      subcategoryLabel: 'Cinéma',
      stock: {
        id: 825,
        beginningDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
        isBookable: true,
        price: 140000,
      },
      venue: {
        id: 1,
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
      contactEmail: '',
      contactPhone: '',
      domains: [],
      offerVenue: {
        venueId: 1,
        otherAddress: '',
        addressType: OfferAddressType.OFFERER_VENUE,
      },
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
      interventionArea: ['75', '92'],
    }

    offerInCayenne = {
      id: 480,
      description: 'Une offre vraiment coco',
      name: 'Coco channel',
      subcategoryLabel: 'Cinéma',
      stock: {
        id: 826,
        beginningDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        isBookable: true,
        price: 80000,
      },
      venue: {
        id: 1,
        address: '1 boulevard Poissonnière',
        city: 'Cayenne',
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
      contactEmail: '',
      contactPhone: '',
      domains: [],
      offerVenue: {
        venueId: 1,
        otherAddress: '',
        addressType: OfferAddressType.OFFERER_VENUE,
      },
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
      interventionArea: ['973'],
    }

    otherOffer = {
      id: 481,
      description: 'Une autre offre',
      name: 'Un autre titre',
      subcategoryLabel: 'Cinéma',
      stock: {
        id: 827,
        beginningDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        isBookable: true,
        price: 3000,
      },
      venue: {
        id: 1,
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
      contactEmail: '',
      contactPhone: '',
      domains: [],
      offerVenue: {
        venueId: 1,
        otherAddress: '',
        addressType: OfferAddressType.OFFERER_VENUE,
      },
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
      interventionArea: ['75', '92'],
    }

    offersProps = {
      handleResetFiltersAndLaunchSearch: jest.fn(),
      hits: searchFakeResults,
      setIsLoading: jest.fn(),
      userRole: AdageFrontRoles.REDACTOR,
      refineNext: jest.fn(),
      hasMore: true,
      hasPrevious: false,
      refinePrevious: jest.fn(),
      nbHits: 2,
      nbSortedHits: 0,
      areHitsSorted: true,
      processingTimeMS: 0,
    }
  })

  it('should display two offers with their respective stocks when two bookable offers', async () => {
    // Given
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInParis)
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInCayenne)
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
    const { rerender } = renderOffers(offersProps)
    jest.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(otherOffer)
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
      isTemplate: false,
      __queryID: 'queryId',
    }

    // When
    offersProps.hits = [otherSearchResult]
    rerender(<OffersComponent {...offersProps} />)

    // Then
    const otherOfferName = await screen.findByText(otherOffer.name)
    expect(otherOfferName).toBeInTheDocument()
    expect(screen.getAllByTestId('offer-listitem')).toHaveLength(1)
    expect(screen.queryByText(offerInParis.name)).not.toBeInTheDocument()
    expect(screen.queryByText(offerInCayenne.name)).not.toBeInTheDocument()
    expect(screen.getByText('2 résultats')).toBeInTheDocument()
    expect(screen.getByText('Vous avez vu 1 offre sur 2')).toBeInTheDocument()
  })

  it('should show most recent results and cancel previous request', async () => {
    // Given
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(
        new CancelablePromise(resolve =>
          setTimeout(() => resolve(offerInParis), 500)
        )
      )
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInCayenne)
    const { rerender } = renderOffers(offersProps)
    jest.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(otherOffer)
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
      isTemplate: false,
      __queryID: 'queryId',
    }

    // When
    offersProps.hits = [otherSearchResult]
    rerender(<OffersComponent {...offersProps} />)

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
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockImplementationOnce(
        () =>
          new CancelablePromise(resolve =>
            setTimeout(() => resolve(offerInParis), 500)
          )
      )
      .mockImplementationOnce(
        () =>
          new CancelablePromise(resolve =>
            setTimeout(() => resolve(offerInCayenne), 500)
          )
      )

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
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInParis)
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInCayenne)
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
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInParis)
    jest
      .spyOn(apiAdage, 'getCollectiveOffer')
      .mockResolvedValueOnce(offerInCayenne)

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
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInParis)
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInCayenne)
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
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockRejectedValueOnce('Offre inconnue')
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockRejectedValueOnce('Offre inconnue')

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

  describe('load more button', () => {
    it('should refine next hits when clicking on load more button', async () => {
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInParis)
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInCayenne)
      renderOffers(offersProps)
      const loadMoreButton = await screen.findByRole('button', {
        name: 'Voir plus d’offres',
      })

      userEvent.click(loadMoreButton)

      await waitFor(() =>
        expect(offersProps.refineNext).toHaveBeenCalledTimes(1)
      )
    })

    it('should not show button if there is no more result to refine', async () => {
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInParis)
      jest
        .spyOn(apiAdage, 'getCollectiveOffer')
        .mockResolvedValueOnce(offerInCayenne)
      offersProps.hasMore = false
      renderOffers(offersProps)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
      const loadMoreButton = screen.queryByRole('button', {
        name: 'Voir plus d’offres',
      })
      expect(loadMoreButton).not.toBeInTheDocument()
      expect(
        screen.getByText(
          'Vous avez vu toutes les offres qui correspondent à votre recherche.'
        )
      ).toBeInTheDocument()
    })
  })
})
