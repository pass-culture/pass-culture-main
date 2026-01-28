import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as instantSearch from 'react-instantsearch'

import {
  AdageFrontRoles,
  type AuthenticatedResponse,
  CancelablePromise,
  type CollectiveOfferResponseModel,
  EacFormat,
  type ListCollectiveOfferTemplateResponseModel,
  StudentLevels,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import * as useMediaQuery from '@/commons/hooks/useMediaQuery'
import {
  defaultCollectiveOffer,
  defaultUseInfiniteHitsReturn,
  defaultUseStatsReturn,
} from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { Offers, type OffersProps } from './Offers'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useParams: () => ({
    venueId: '',
    siret: '',
  }),
}))

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferTemplates: vi.fn(),
    logSearchButtonClick: vi.fn(),
    logSearchShowMore: vi.fn(),
    logOfferListViewSwitch: vi.fn(),
    logOfferTemplateDetailsButtonClick: vi.fn(),
  },
}))

vi.mock('@/commons/utils/config', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/config')),
    LOGS_DATA: true,
  }
})

const searchFakeResults = [
  {
    objectID: 'T-479',
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
    isTemplate: true,
    __queryID: 'queryId',
    __position: 0,
  },
  {
    objectID: 'T-480',
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
    isTemplate: true,
    __queryID: 'queryId',
    __position: 1,
  },
]

const otherFakeSearchResult = {
  objectID: 'T-481',
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
  isTemplate: true,
  __queryID: 'queryId',
  __position: 0,
}

const mockRefinePagination = vi.fn()

const renderOffers = (
  props: OffersProps,
  adageUser: AuthenticatedResponse,
  options?: RenderWithProvidersOptions
) => {
  vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

  return renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <Offers {...props} />
    </AdageUserContextProvider>,
    options
  )
}

describe('offers', () => {
  let offerInParis: CollectiveOfferResponseModel
  let offerInCayenne: CollectiveOfferResponseModel
  let otherOffer: CollectiveOfferResponseModel
  let offersProps: OffersProps
  let adageUser: AuthenticatedResponse

  beforeEach(() => {
    vi.resetAllMocks()
    vi.mock('react-instantsearch', async () => {
      return {
        ...(await vi.importActual('react-instantsearch')),
        useStats: () => ({
          ...defaultUseStatsReturn,
          nbHits: 2,
        }),
        useInfiniteHits: () => ({
          ...defaultUseInfiniteHitsReturn,
          currentPageHits: searchFakeResults,
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
        usePagination: () => ({
          currentRefinement: 1,
          nbPages: 2,
          refine: mockRefinePagination,
        }),
      }
    })

    adageUser = {
      role: AdageFrontRoles.REDACTOR,
      preferences: { feedback_form_closed: null },
    }

    offerInParis = defaultCollectiveOffer

    offerInCayenne = {
      id: 480,
      description: 'Une offre vraiment coco',
      name: 'Coco channel',
      stock: {
        id: 826,
        startDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
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
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
      interventionArea: ['973'],
      formats: [EacFormat.CONCERT],
      isTemplate: false,
    }

    otherOffer = {
      id: 481,
      description: 'Une autre offre',
      name: 'Un autre titre',
      stock: {
        id: 827,
        startDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
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
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
      interventionArea: ['75', '92'],
      formats: [EacFormat.CONCERT],
      isTemplate: false,
    }

    offersProps = {
      submitCount: 0,
      indexId: 'test-props-value',
    }
  })

  it('should display two offers with their respective stocks when two bookable offers', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })

    // When
    renderOffers(offersProps, adageUser)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)
    expect(screen.getByText(offerInParis.name)).toBeInTheDocument()
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
    expect(screen.getByText('2 offres au total')).toBeInTheDocument()
  })

  it('should remove previous rendered offers on results update', async () => {
    const { rerender } = renderOffers(offersProps, adageUser)

    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [otherOffer],
    })

    vi.spyOn(instantSearch, 'useStats').mockImplementation(() => ({
      ...defaultUseStatsReturn,
      nbHits: 1,
    }))

    vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementationOnce(() => ({
      ...defaultUseInfiniteHitsReturn,
      currentPageHits: searchFakeResults,
    }))

    vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementation(() => ({
      ...defaultUseInfiniteHitsReturn,
      currentPageHits: [otherFakeSearchResult],
    }))

    // When
    rerender(
      <AdageUserContextProvider adageUser={adageUser}>
        <Offers {...offersProps} />
      </AdageUserContextProvider>
    )

    // Then
    expect(await screen.findByText(otherOffer.name)).toBeInTheDocument()

    expect(screen.queryByText(offerInParis.name)).not.toBeInTheDocument()
    expect(screen.queryByText(offerInCayenne.name)).not.toBeInTheDocument()

    expect(screen.getByText('1 offre au total')).toBeInTheDocument()
  })

  it('should show a loader while waiting for response', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates')
      .mockImplementationOnce(
        () =>
          new CancelablePromise<ListCollectiveOfferTemplateResponseModel>(
            (resolve) =>
              setTimeout(
                () => resolve({ collectiveOffers: [offerInParis] }),
                500
              )
          )
      )
      .mockImplementationOnce(
        () =>
          new CancelablePromise<ListCollectiveOfferTemplateResponseModel>(
            (resolve) =>
              setTimeout(
                () => resolve({ collectiveOffers: [offerInCayenne] }),
                500
              )
          )
      )

    // When
    renderOffers(offersProps, adageUser)

    // Then
    expect(screen.getAllByTestId('spinner').length).toBeGreaterThanOrEqual(1)

    const offerInParisName = await screen.findByText(offerInParis.name)
    expect(offerInParisName).toBeInTheDocument()
  })

  it('should display only non sold-out offers', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [
        {
          ...offerInParis,
          isSoldOut: true,
        },
        offerInCayenne,
      ],
    })

    renderOffers(offersProps, adageUser)

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  it('should not display expired offer', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [
        {
          ...offerInParis,
          isExpired: true,
        },
        offerInCayenne,
      ],
    })

    // When
    renderOffers(offersProps, adageUser)

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)
    expect(screen.getByText(offerInCayenne.name)).toBeInTheDocument()
  })

  it('should display survey satisfaction', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })

    // When
    renderOffers(offersProps, adageUser)

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)

    // Then
    const surveySatisfaction = screen.getByText('Enquête de satisfaction')
    expect(surveySatisfaction).toBeInTheDocument()
  })

  it('should not display survey satisfaction if user role readonly', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })
    // When
    renderOffers(offersProps, { ...adageUser, role: AdageFrontRoles.READONLY })

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)

    // Then
    const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  it('should not display survey satisfaction if only 1 offer', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [otherOffer],
    })

    vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementation(() => ({
      ...defaultUseInfiniteHitsReturn,
      currentPageHits: defaultUseInfiniteHitsReturn.hits.slice(0, 1),
    }))

    // When
    renderOffers(offersProps, adageUser)

    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(1)

    // Then
    const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  it('should not display survey satisfaction', async () => {
    // Given
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })

    // When
    renderOffers(offersProps, {
      ...adageUser,
      preferences: { feedback_form_closed: true },
    })

    // Then
    const listItemsInOffer = await screen.findAllByTestId('offer-listitem')
    expect(listItemsInOffer).toHaveLength(2)
    const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
    expect(surveySatisfaction).not.toBeInTheDocument()
  })

  describe('should display no results page', () => {
    it('when there are no results', async () => {
      vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementation(() => ({
        ...defaultUseInfiniteHitsReturn,
        currentPageHits: [],
      }))
      // When
      renderOffers({ ...offersProps }, adageUser)

      // Then
      const errorMessage = await screen.findByText(
        'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })

    it('when all offers are not bookable', async () => {
      // Given
      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
        collectiveOffers: [
          { ...offerInCayenne, isExpired: true },
          { ...offerInParis, isSoldOut: true },
        ],
      })
      // When
      renderOffers(offersProps, adageUser)

      // Then
      const errorMessage = await screen.findByText(
        'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })

    it('when offers are not found', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockRejectedValueOnce(
        'Offre inconnue'
      )

      renderOffers(offersProps, adageUser)

      const errorMessage = await screen.findByText(
        'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
      )
      expect(errorMessage).toBeInTheDocument()
      const listItemsInOffer = screen.queryAllByTestId('offer-listitem')
      expect(listItemsInOffer).toHaveLength(0)
    })
  })

  describe('load more button', () => {
    it('should not show diffuse help', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
        collectiveOffers: [offerInParis, offerInCayenne],
      })

      renderOffers(offersProps, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const diffuseHelp = screen.queryByText('Le saviez-vous ?')

      expect(diffuseHelp).not.toBeInTheDocument()
    })

    it('should show diffuse help', async () => {
      vi.spyOn(global.Date, 'now').mockImplementation(() =>
        new Date('2025-08-15T00:00:00Z').getTime()
      )

      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
        collectiveOffers: [offerInParis, offerInCayenne],
      })

      renderOffers({ ...offersProps, submitCount: 1 }, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const diffuseHelp = screen.getByText('Le saviez-vous ?')

      expect(diffuseHelp).toBeInTheDocument()
    })

    it('should hide diffuse help before the filters were applied at least once', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
        collectiveOffers: [offerInParis, offerInCayenne],
      })

      renderOffers({ ...offersProps, submitCount: 0 }, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(screen.queryByText('Le saviez-vous ?')).not.toBeInTheDocument()
    })

    it('should display back to top button if filters are not visible', async () => {
      vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
        collectiveOffers: [offerInParis, offerInCayenne],
      })
      renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(
        screen.getByRole('link', { name: /Retour en haut/ })
      ).toBeInTheDocument()
    })
  })

  it('should show the offer cards', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })
    renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('link', { name: offerInParis.name })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: offerInCayenne.name })
    ).toBeInTheDocument()
  })

  it('should enable grid vue on toggle click', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInParis, offerInCayenne],
    })
    renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Une offre vraiment chouette')).toBeInTheDocument()

    const gridVue = screen.getByTestId('toggle-button')

    await userEvent.click(gridVue)

    expect(
      screen.queryByText('Une offre vraiment chouette')
    ).not.toBeInTheDocument()
  })

  it('should change to grid vue when breakpoint active', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(offerInParis)
    vi.spyOn(apiAdage, 'getCollectiveOffer').mockResolvedValueOnce(
      offerInCayenne
    )
    renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByText('Une offre vraiment chouette')
    ).not.toBeInTheDocument()
  })

  it('should trigger a log event when clicking the offer when the offers are in list mode', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [otherOffer],
    })

    vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementation(() => ({
      ...defaultUseInfiniteHitsReturn,
      currentPageHits: [otherFakeSearchResult],
    }))

    renderOffers(offersProps, adageUser)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const link = screen.getByRole('link', {
      name: 'Un autre titre',
    })
    link.addEventListener('click', (e) => {
      e.preventDefault()
    })
    await userEvent.click(link)

    expect(apiAdage.logOfferTemplateDetailsButtonClick).toHaveBeenCalled()
  })

  it('should trigger a log event when clicking the offer when the offers are in grid mode', async () => {
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [otherOffer],
    })

    vi.spyOn(instantSearch, 'useInfiniteHits').mockImplementation(() => ({
      ...defaultUseInfiniteHitsReturn,
      currentPageHits: [otherFakeSearchResult],
    }))

    renderOffers(offersProps, adageUser)
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValueOnce(true)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const link = screen.getByRole('link', {
      name: 'Un autre titre Un autre lieu',
    })

    link.addEventListener('click', (e) => {
      e.preventDefault()
    })
    await userEvent.click(link)

    expect(apiAdage.logOfferTemplateDetailsButtonClick).toHaveBeenCalled()
  })

  it('should call tracker when clicking on toggle button view', async () => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: () => ({
        matches: true,
        addListener: vi.fn(),
        removeListener: vi.fn(),
      }),
    })
    vi.spyOn(apiAdage, 'getCollectiveOfferTemplates').mockResolvedValueOnce({
      collectiveOffers: [offerInCayenne, offerInParis],
    })
    renderOffers({ ...offersProps, isBackToTopVisibile: true }, adageUser)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const toggleButtonView = screen.getByTestId('toggle-button')

    await userEvent.click(toggleButtonView)

    expect(apiAdage.logOfferListViewSwitch).toHaveBeenCalledWith(
      expect.objectContaining({ iframeFrom: '/', source: 'list' })
    )
  })
})
