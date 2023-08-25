import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  AdageFrontRoles,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/adage'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { HydratedCollectiveOffer } from 'pages/AdageIframe/app/types/offers'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offer, { OfferProps } from '../Offer'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logOfferDetailsButtonClick: vi.fn(),
    logOfferTemplateDetailsButtonClick: vi.fn(),
    logFavOfferButtonClick: vi.fn(),
    logContactModalButtonClick: vi.fn(),
  },
}))
vi.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

vi.mock('react-instantsearch-dom', () => {
  return {
    ...vi.importActual('react-instantsearch-dom'),
    connectStats: vi.fn(Component => (props: any) => (
      <Component
        {...props}
        areHitsSorted={false}
        nbHits={0}
        nbSortedHits={0}
        processingTimeMS={0}
      />
    )),
    Stats: vi.fn(() => <div>2 résultats</div>),
  }
})

const user = {
  role: AdageFrontRoles.REDACTOR,
  email: 'test@example.com',
  departmentCode: '75',
}

const renderOffers = (
  props: OfferProps,
  featuresOverride?: { nameKey: string; isActive: boolean }[]
) => {
  renderWithProviders(
    <AdageUserContext.Provider value={{ adageUser: user }}>
      <Offer {...props} />
    </AdageUserContext.Provider>,
    {
      storeOverrides: {
        features: {
          list: featuresOverride,
          initialized: true,
        },
      },
    }
  )
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
      nationalProgram: { name: 'Program Test', id: 123 },
    }
    offerProps = {
      offer: offerInParis,
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

      // First summary line
      expect(screen.getByText('Cinéma')).toBeInTheDocument()

      expect(screen.getByText('75000, Paris')).toBeInTheDocument()
      // second summary line
      expect(screen.getByText('16/09/2022 à 02:00')).toBeInTheDocument()
      expect(screen.getByText('Jusqu’à 10 places')).toBeInTheDocument()
      expect(screen.getByText('1 400,00 €')).toBeInTheDocument()
      expect(screen.getByText('Multi niveaux')).toBeInTheDocument()

      // Info that are in offer details component
      expect(
        screen.queryByText('Moteur', { exact: false })
      ).not.toBeInTheDocument()
    })

    it('should show all offer informations if user click on "en savoir plus"', async () => {
      // When
      renderOffers({ ...offerProps, offer: offerInCayenne }, [
        {
          isActive: true,
          nameKey: 'WIP_ENABLE_NATIONAL_SYSTEM',
        },
      ])

      const offerName = await screen.findByText(offerInCayenne.name)
      expect(offerName).toBeInTheDocument()

      // First summary line
      expect(screen.getByText('Cinéma')).toBeInTheDocument()

      expect(screen.getByText('A la mairie')).toBeInTheDocument()

      // second summary line
      expect(screen.getByText('25/09/2021 à 19:00')).toBeInTheDocument()
      expect(
        screen.queryByText('Jusqu’à', { exact: false })
      ).not.toBeInTheDocument()
      expect(screen.getByText('Gratuit')).toBeInTheDocument()
      expect(screen.getByText('Collège - 4e')).toBeInTheDocument()

      const seeMoreButton = await screen.findByRole('button', {
        name: 'en savoir plus',
      })
      userEvent.click(seeMoreButton)

      await waitFor(() => {
        expect(screen.queryByText('Le détail de mon prix')).toBeInTheDocument()
      })

      // Info that are in offer details component
      expect(screen.queryByText('Dispositif National')).toBeInTheDocument()
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
          https://lien2.com et https://lien3.com
          https://\nurl.com https://unlien avecuneespace
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
      expect((links[2] as HTMLLinkElement).href).toBe('https://lien3.com/')
      expect((links[3] as HTMLLinkElement).href).toBe('https://')
      expect((links[4] as HTMLLinkElement).href).toBe('https://unlien/')
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

    it('should display request form modal', async () => {
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

      expect(screen.getByText('Contacter le partenaire culturel'))
    })

    it('should display distance when offer has coordinates and FF is active', async () => {
      renderOffers(
        {
          ...offerProps,
          offer: {
            ...offerInParis,
            venue: {
              ...offerInParis.venue,
              coordinates: { latitude: 1, longitude: 1 },
            },
          },
        },
        [{ nameKey: 'WIP_ENABLE_ADAGE_GEO_LOCATION', isActive: true }]
      )

      // Distance between {0, 0} and {1, 1} is 157km
      expect(
        screen.getByText('basé à 157 km de votre établissement')
      ).toBeInTheDocument()
    })

    it('should display can move in your institution is offer intervention area match user one', async () => {
      renderOffers(
        {
          ...offerProps,
          offer: {
            ...offerInParis,
            venue: {
              ...offerInParis.venue,
              coordinates: { latitude: 1, longitude: 1 },
            },
            offerVenue: {
              venueId: null,
              otherAddress: 'A la mairie',
              addressType: OfferAddressType.OTHER,
            },
            interventionArea: ['75'],
          },
        },
        [{ nameKey: 'WIP_ENABLE_ADAGE_GEO_LOCATION', isActive: true }]
      )

      expect(
        screen.getByText('peut se déplacer dans votre département')
      ).toBeInTheDocument()
    })
  })
})
