import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'
import { QueryCache, QueryClient, QueryClientProvider } from 'react-query'

import { api } from 'api/api'
import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'api/gen'
import {
  OffersComponent as Offers,
  OffersComponentProps,
} from 'app/components/OffersInstantSearch/OffersSearch/Offers/Offers'
import {
  FiltersContextProvider,
  AlgoliaQueryContextProvider,
} from 'app/providers'
import { ResultType } from 'utils/types'

jest.mock('api/api', () => ({
  api: { getAdageIframeGetCollectiveOffer: jest.fn() },
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

const mockedPcapi = api as jest.Mocked<typeof api>

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
  isTemplate: false,
  _highlightResult: {},
}

const renderOffers = (props: OffersComponentProps) =>
  render(
    <FiltersContextProvider>
      <AlgoliaQueryContextProvider>
        <Offers {...props} />
      </AlgoliaQueryContextProvider>
    </FiltersContextProvider>,
    { wrapper }
  )

describe('offer', () => {
  let offerInParis: CollectiveOfferResponseModel
  let offerInCayenne: CollectiveOfferResponseModel
  let offersProps: OffersComponentProps

  beforeEach(() => {
    queryCache.clear()
    offerInParis = {
      id: 479,
      description: 'Une offre vraiment chouette',
      name: 'Une chouette à la mer',
      subcategoryLabel: 'Cinéma',
      stock: {
        id: 825,
        beginningDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
        isBookable: true,
        price: 140000,
        numberOfTickets: 10,
      },

      venue: {
        id: 1,
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
      offerVenue: {
        venueId: 'VENUE_ID',
        otherAddress: '',
        addressType: OfferAddressType.OffererVenue,
      },
      students: [StudentLevels.Collge4e, StudentLevels.Collge3e],
      isSoldOut: false,
      isExpired: false,
      audioDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      contactEmail: '',
      contactPhone: '',
      domains: [],
      interventionArea: ['75', '92'],
    }

    offerInCayenne = {
      id: 479,
      description: 'Une offre vraiment chouette',
      name: 'Une chouette à la mer',
      subcategoryLabel: 'Cinéma',
      stock: {
        id: 825,
        beginningDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        bookingLimitDatetime: new Date('2021-09-25T22:00:00Z').toISOString(),
        isBookable: true,
        price: 0,
      },
      educationalPriceDetail: 'Le détail de mon prix',
      venue: {
        id: 1,
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
      offerVenue: {
        venueId: '',
        otherAddress: 'A la mairie',
        addressType: OfferAddressType.Other,
      },
      students: [StudentLevels.Collge4e],
      isSoldOut: false,
      isExpired: false,
      audioDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      contactEmail: '',
      contactPhone: '',
      domains: [],
      interventionArea: ['973'],
    }

    offersProps = {
      hits: [searchFakeResult],
      setIsLoading: jest.fn(),
      userRole: AdageFrontRoles.Redactor,
      handleResetFiltersAndLaunchSearch: jest.fn(),
    }
  })

  describe('offer item', () => {
    it('should not show all information at first', async () => {
      // Given
      mockedPcapi.getAdageIframeGetCollectiveOffer.mockResolvedValue(
        offerInParis
      )

      // When
      renderOffers(offersProps)

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()
      const listItemsInOffer = screen.getAllByTestId('offer-listitem')
      const summaryAndDomainList = within(listItemsInOffer[0]).getAllByRole(
        'list'
      )
      expect(summaryAndDomainList).toHaveLength(3)

      // First summary line
      expect(
        within(summaryAndDomainList[1]).getByText('Cinéma')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[1]).getByText('16/09/2022 à 02:00')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[1]).getByText('75000, Paris')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryAndDomainList[2]).getByText('Jusqu’à 10 places')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[2]).getByText('1 400,00 €')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[2]).getByText('Multi niveaux')
      ).toBeInTheDocument()

      // Info that are in offer details component
      expect(
        screen.queryByText('Moteur', { exact: false })
      ).not.toBeInTheDocument()
    })

    it('should show all offer informations if user click on "en savoir plus"', async () => {
      // Given
      mockedPcapi.getAdageIframeGetCollectiveOffer.mockResolvedValue(
        offerInCayenne
      )

      // When
      renderOffers(offersProps)

      const offerName = await screen.findByText(offerInCayenne.name)
      expect(offerName).toBeInTheDocument()
      const listItemsInOffer = screen.getAllByTestId('offer-listitem')
      const summaryAndDomainList = within(listItemsInOffer[0]).getAllByRole(
        'list'
      )
      expect(summaryAndDomainList).toHaveLength(3)

      // First summary line
      expect(
        within(summaryAndDomainList[1]).getByText('Cinéma')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[1]).getByText('25/09/2021 à 19:00')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[1]).getByText('A la mairie')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryAndDomainList[2]).queryByText('Jusqu’à', { exact: false })
      ).not.toBeInTheDocument()
      expect(
        within(summaryAndDomainList[2]).getByText('Gratuit')
      ).toBeInTheDocument()
      expect(
        within(summaryAndDomainList[2]).getByText('Collège - 4e')
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
      expect(
        screen.queryByText('Zone de Mobiltié de l’acteur culturel')
      ).toBeInTheDocument()
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

    it('should format the description when links are present', async () => {
      // Given
      mockedPcapi.getAdageIframeGetCollectiveOffer.mockResolvedValue({
        ...offerInParis,
        description: `lien 1 : www.lien1.com
          https://lien2.com et http://lien3.com
          https://\nurl.com http://unlien avecuneespace
          contact: toto@toto.com`,
      })

      // When
      renderOffers(offersProps)

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()

      const descriptionParagraph = await screen.findByText('lien 1', {
        exact: false,
        selector: 'p',
      })

      const links = within(descriptionParagraph).getAllByRole('link')

      expect(links).toHaveLength(6)
      expect((links[0] as HTMLLinkElement).href).toBe('https://www.lien1.com/')
      expect((links[0] as HTMLLinkElement).childNodes[0].nodeValue).toBe(
        'www.lien1.com'
      )
      expect((links[1] as HTMLLinkElement).href).toBe('https://lien2.com/')
      expect((links[2] as HTMLLinkElement).href).toBe('http://lien3.com/')
      expect((links[3] as HTMLLinkElement).href).toBe('https://')
      expect((links[4] as HTMLLinkElement).href).toBe('http://unlien/')
      expect((links[5] as HTMLLinkElement).href).toBe('mailto:toto@toto.com')
    })
  })
})
