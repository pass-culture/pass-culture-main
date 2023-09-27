import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
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
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'
import { ResultType } from 'utils/types'

import { OffersComponent, OffersComponentProps } from '../Offers'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getCollectiveOffer: vi.fn(),
    logSearchButtonClick: vi.fn(),
    logTrackingFilter: vi.fn(),
  },
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

const renderOffers = (
  props: OffersComponentProps,
  adageUser: AuthenticatedResponse,
  storeOverrides = {}
) => {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <AlgoliaQueryContextProvider>
        <FacetFiltersContextProvider>
          <Formik onSubmit={() => {}} initialValues={{}}>
            <OffersComponent {...props} />
          </Formik>
        </FacetFiltersContextProvider>
      </AlgoliaQueryContextProvider>
    </AdageUserContextProvider>,
    {
      storeOverrides,
    }
  )
}

describe('offers', () => {
  let offerInParis: CollectiveOfferResponseModel
  let offerInCayenne: CollectiveOfferResponseModel
  let otherOffer: CollectiveOfferResponseModel
  let offersProps: OffersComponentProps
  let adageUser: AuthenticatedResponse

  beforeEach(() => {
    adageUser = {
      role: AdageFrontRoles.REDACTOR,
      preferences: { feedback_form_closed: null },
    }

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
      isFavorite: false,
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
      isFavorite: false,
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
      isFavorite: false,
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
      handleResetFiltersAndLaunchSearch: vi.fn(),
      hits: searchFakeResults,
      setIsLoading: vi.fn(),
      refineNext: vi.fn(),
      hasMore: true,
      hasPrevious: false,
      refinePrevious: vi.fn(),
      nbHits: 2,
      nbSortedHits: 0,
      areHitsSorted: true,
      processingTimeMS: 0,
      submitCount: 0,
    }
  })

  it('should display two offers with their respective stocks when two bookable offers', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(offerInParis)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )
    // When
    renderOffers(offersProps, adageUser)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)
    expect(screen.getByText(offerInParis.name)).toBeInTheDocument()
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
    expect(screen.getByText('2 résultats')).toBeInTheDocument()
  })

  it('should remove previous rendered offers on results update', async () => {
    const { rerender } = renderOffers(offersProps, adageUser)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(otherOffer)
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
    offersProps = { ...offersProps, hits: [otherSearchResult] }
    rerender(
      <AdageUserContextProvider adageUser={adageUser}>
        <OffersComponent {...offersProps} />
      </AdageUserContextProvider>
    )

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
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockImplementationOnce(
      () =>
        new CancelablePromise<CollectiveOfferResponseModel>(resolve =>
          setTimeout(() => resolve(offerInParis), 500)
        )
    )
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )
    const { rerender } = renderOffers(offersProps, adageUser)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(otherOffer)
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
    offersProps = { ...offersProps, hits: [otherSearchResult] }
    rerender(
      <AdageUserContextProvider adageUser={adageUser}>
        <OffersComponent {...offersProps} />
      </AdageUserContextProvider>
    )

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
    vi.spyOn(apiAdage, 'getCollectiveOffer')
      .mockImplementationOnce(
        () =>
          new CancelablePromise<CollectiveOfferResponseModel>(resolve =>
            setTimeout(() => resolve(offerInParis), 500)
          )
      )
      .mockImplementationOnce(
        () =>
          new CancelablePromise<CollectiveOfferResponseModel>(resolve =>
            setTimeout(() => resolve(offerInCayenne), 500)
          )
      )

    // When
    renderOffers(offersProps, adageUser)

    // Then
    const loader = await screen.findByText('Recherche en cours')
    expect(loader).toBeInTheDocument()
    const offerInParisName = await screen.findByText(offerInParis.name)
    expect(offerInParisName).toBeInTheDocument()
  })

  it('should display only non sold-out offers', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce({
      ...offerInParis,
      isSoldOut: true,
    })
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )
    // When
    renderOffers(offersProps, adageUser)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  it('should not display expired offer', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce({
      ...offerInParis,
      isExpired: true,
    })
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )

    // When
    renderOffers(offersProps, adageUser)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  it('should not display survey satisfaction ff not active', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(offerInParis)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )

    // When
    renderOffers(offersProps, adageUser, {
      features: {
        list: [{ isActive: false, nameKey: 'WIP_ENABLE_SATISFACTION_SURVEY' }],
      },
    })

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)

    // Then
    const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  it('should display survey satisfaction', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(offerInParis)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )

    // When
    renderOffers(offersProps, adageUser, {
      features: {
        list: [{ isActive: true, nameKey: 'WIP_ENABLE_SATISFACTION_SURVEY' }],
      },
    })

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)

    // Then
    const surveySatisfaction = screen.getByText('Enquête de satisfaction')
    expect(surveySatisfaction).toBeInTheDocument()
  })

  it('should not display survey satisfaction if only 1 offer', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce({
      ...offerInParis,
      isExpired: true,
    })
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )
    // When
    renderOffers(offersProps, adageUser, {
      features: {
        list: [{ isActive: true, nameKey: 'WIP_ENABLE_SATISFACTION_SURVEY' }],
      },
    })

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)

    // Then
    const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  it('should not display survey satisfaction', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(offerInParis)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )

    // When
    renderOffers(
      offersProps,
      {
        ...adageUser,
        preferences: { feedback_form_closed: true },
      },
      {
        features: {
          list: [{ isActive: true, nameKey: 'WIP_ENABLE_SATISFACTION_SURVEY' }],
        },
      }
    )

    // Then
    const surveySatisfaction = await screen.queryByText(
      'Enquête de satisfaction'
    )
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  describe('should display no results page', () => {
    it('when there are no results', async () => {
      // When
      renderOffers({ ...offersProps, hits: [] }, adageUser)

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
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce({
        ...offerInParis,
        isExpired: true,
      })
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce({
        ...offerInCayenne,
        isSoldOut: true,
      })
      // When
      renderOffers(offersProps, adageUser)

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
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce(
        'Offre inconnue'
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockRejectedValueOnce(
        'Offre inconnue'
      )

      // When
      renderOffers(offersProps, adageUser)

      // Then
      const errorMessage = await screen.findByText(
        'Aucun résultat trouvé pour cette recherche.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })

    it('should log filters on new search', async () => {
      const mockLogTrackingFilter = vi.fn()
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      renderOffers(
        { ...offersProps, logFiltersOnSearch: mockLogTrackingFilter },
        adageUser,
        {
          features: {
            list: [{ isActive: true, nameKey: 'WIP_ENABLE_NEW_ADAGE_FILTERS' }],
          },
        }
      )
      expect(mockLogTrackingFilter).toHaveBeenCalledWith(2, 'queryId')
    })
  })

  describe('load more button', () => {
    it('should refine next hits when clicking on load more button', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )
      renderOffers(offersProps, adageUser)
      const loadMoreButton = await screen.findByRole('button', {
        name: 'Voir plus d’offres',
      })

      userEvent.click(loadMoreButton)

      await waitFor(() =>
        expect(offersProps.refineNext).toHaveBeenCalledTimes(1)
      )
    })

    it('should not show button if there is no more result to refine', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )
      renderOffers({ ...offersProps, hasMore: false }, adageUser)
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

    it('should not show diffuse help', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )

      renderOffers(offersProps, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const diffuseHelp = screen.queryByText('Le saviez-vous ?')

      expect(diffuseHelp).not.toBeInTheDocument()
    })

    it('should not show diffuse help on first render', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )

      renderOffers({ ...offersProps, submitCount: 0 }, adageUser, {
        features: {
          list: [{ isActive: true, nameKey: 'WIP_ENABLE_DIFFUSE_HELP' }],
        },
      })
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const diffuseHelp = screen.queryByText('Le saviez-vous ?')

      expect(diffuseHelp).not.toBeInTheDocument()
    })

    it('should show diffuse help', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )

      renderOffers({ ...offersProps, submitCount: 1 }, adageUser, {
        features: {
          list: [{ isActive: true, nameKey: 'WIP_ENABLE_DIFFUSE_HELP' }],
        },
      })
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const diffuseHelp = screen.getByText('Le saviez-vous ?')

      expect(diffuseHelp).toBeInTheDocument()
    })

    it('should display back to top button if filters are not visible', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInParis
      )
      vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
        offerInCayenne
      )
      renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(
        screen.getByRole('link', { name: /Retour en haut/ })
      ).toBeInTheDocument()
    })
  })
})
