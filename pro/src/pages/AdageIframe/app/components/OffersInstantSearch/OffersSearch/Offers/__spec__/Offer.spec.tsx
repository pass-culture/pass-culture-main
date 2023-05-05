import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { OfferAddressType, StudentLevels } from 'apiClient/adage'
import { HydratedCollectiveOffer } from 'pages/AdageIframe/app/types/offers'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offer, { OfferProps } from '../Offer'

jest.mock('apiClient/api', () => ({
  apiAdage: {
    logOfferDetailsButtonClick: jest.fn(),
    logOfferTemplateDetailsButtonClick: jest.fn(),
    logFavOfferButtonClick: jest.fn(),
    logContactModalButtonClick: jest.fn(),
  },
}))
jest.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

jest.mock('react-instantsearch-dom', () => {
  return {
    ...jest.requireActual('react-instantsearch-dom'),
    connectStats: jest.fn(Component => (props: any) => (
      <Component
        {...props}
        areHitsSorted={false}
        nbHits={0}
        nbSortedHits={0}
        processingTimeMS={0}
      />
    )),
    Stats: jest.fn(() => <div>2 résultats</div>),
  }
})

const renderOffers = (
  props: OfferProps,
  featuresOverride?: { nameKey: string; isActive: boolean }[]
) => {
  renderWithProviders(<Offer {...props} />, {
    storeOverrides: {
      features: {
        list: featuresOverride,
        initialized: true,
      },
    },
  })
}

describe('offer', () => {
  let offerInParis: HydratedCollectiveOffer
  let offerInCayenne: HydratedCollectiveOffer
  let offerProps: OfferProps
  beforeEach(() => {
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
        venueId: 1,
        otherAddress: '',
        addressType: OfferAddressType.OFFERER_VENUE,
      },
      students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
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
      teacher: {
        firstName: 'Jean',
        lastName: 'Dupont',
      },
      isTemplate: false,
    }
    offerInCayenne = {
      id: 480,
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
        venueId: null,
        otherAddress: 'A la mairie',
        addressType: OfferAddressType.OTHER,
      },
      students: [StudentLevels.COLL_GE_4E],
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
      isTemplate: false,
    }
    offerProps = {
      offer: offerInParis,
      canPrebookOffers: true,
      queryId: '1',
      position: 1,
    }
  })

  describe('offer item', () => {
    it('should not show all information at first', async () => {
      // When
      renderOffers(offerProps)

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()
      const redactorName = screen.getByText('Jean Dupont')
      expect(redactorName).toBeInTheDocument()
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
        within(summaryAndDomainList[1]).getByText('75000, Paris')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryAndDomainList[2]).getByText('16/09/2022 à 02:00')
      ).toBeInTheDocument()
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
      // When
      renderOffers({ ...offerProps, offer: offerInCayenne })

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
        within(summaryAndDomainList[1]).getByText('A la mairie')
      ).toBeInTheDocument()
      // second summary line
      expect(
        within(summaryAndDomainList[2]).getByText('25/09/2021 à 19:00')
      ).toBeInTheDocument()
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
      expect(screen.queryByText('Zone de Mobilité')).toBeInTheDocument()
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

      // When
      renderOffers({
        ...offerProps,
        offer: {
          ...offerInParis,
          description: `lien 1 : www.lien1.com
          https://lien2.com et http://lien3.com
          https://\nurl.com http://unlien avecuneespace
          contact: toto@toto.com`,
        },
      })

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

    it('should display modal when clicking like button', async () => {
      renderOffers(
        {
          ...offerProps,
          offer: { ...offerInParis, domains: [{ id: 1, name: 'CINEMA' }] },
        },
        [{ nameKey: 'WIP_ENABLE_LIKE_IN_ADAGE', isActive: true }]
      )

      const likeButton = await screen.getByTitle("bouton j'aime")
      await userEvent.click(likeButton)

      expect(
        screen.getByText(
          /Lʼéquipe du pass Culture a bien noté votre intérêt pour cette fonctionnalité. Elle arrivera bientôt !/
        )
      ).toBeInTheDocument()
    })

    it('should close modal when clicking close button', async () => {
      renderOffers(offerProps, [
        { nameKey: 'WIP_ENABLE_LIKE_IN_ADAGE', isActive: true },
      ])

      const likeButton = await screen.getByTitle("bouton j'aime")
      await userEvent.click(likeButton)

      const closeButton = await screen.getByRole('button', { name: 'Fermer' })
      await userEvent.click(closeButton)

      expect(
        screen.queryByText(
          /Lʼéquipe du pass Culture a bien noté votre intérêt pour cette fonctionnalité. Elle arrivera bientôt !/
        )
      ).not.toBeInTheDocument()
    })

    it('should display request form modal with venue public name', async () => {
      renderOffers(
        {
          ...offerProps,
          offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
        },
        [{ nameKey: 'WIP_ENABLE_COLLECTIVE_REQUEST', isActive: true }]
      )

      const contactButton = screen.getByRole('button', {
        name: 'Contacter',
      })
      await userEvent.click(contactButton)

      expect(screen.getByText('Mon lieu nom publique - Ma super structure'))
    })

    it('should display request form modal with venue name if venue has no public name', async () => {
      renderOffers(
        {
          ...offerProps,
          offer: {
            ...defaultCollectiveTemplateOffer,
            venue: {
              ...defaultCollectiveTemplateOffer.venue,
              publicName: '',
            },
            isTemplate: true,
          },
        },
        [{ nameKey: 'WIP_ENABLE_COLLECTIVE_REQUEST', isActive: true }]
      )

      const contactButton = screen.getByRole('button', {
        name: 'Contacter',
      })
      await userEvent.click(contactButton)

      expect(screen.getByText('Mon lieu - Ma super structure'))
    })
  })
})
