import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  EacFormat,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { Offer, OfferProps } from '../Offer'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logOfferDetailsButtonClick: vi.fn(),
    logOfferTemplateDetailsButtonClick: vi.fn(),
    logFavOfferButtonClick: vi.fn(),
    logContactModalButtonClick: vi.fn(),
    logTrackingMap: vi.fn(),
    postCollectiveOfferFavorites: vi.fn().mockImplementation(() => {}),
    postCollectiveTemplateFavorites: vi.fn().mockImplementation(() => {}),
    deleteFavoriteForCollectiveOffer: vi.fn().mockImplementation(() => {}),
    deleteFavoriteForCollectiveOfferTemplate: vi
      .fn()
      .mockImplementation(() => {}),
  },
}))
vi.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

vi.mock('utils/config', async () => {
  return {
    ...(await vi.importActual('utils/config')),
    LOGS_DATA: true,
  }
})

const user: AuthenticatedResponse = {
  role: AdageFrontRoles.REDACTOR,
  email: 'test@example.com',
  departmentCode: '75',
  lat: null,
  lon: null,
}

const renderOffer = (
  props: OfferProps,
  adageUser: AuthenticatedResponse | null = user,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <Offer {...props} />
    </AdageUserContextProvider>,
    options
  )
}

describe('offer', () => {
  let offerInParis: CollectiveOfferResponseModel
  let offerInCayenne: CollectiveOfferResponseModel
  let offerProps: OfferProps
  beforeEach(() => {
    offerInParis = { ...defaultCollectiveOffer, isTemplate: false }
    offerInCayenne = {
      id: 480,
      description: 'Une offre vraiment chouette',
      name: 'Une chouette à la mer',
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
      isFavorite: false,
      audioDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      contactEmail: '',
      contactPhone: '',
      domains: [{ id: 1, name: 'Super domaine' }],
      interventionArea: ['973'],
      isTemplate: false,
      nationalProgram: { name: 'Program Test', id: 123 },
      imageUrl: 'url',
      formats: [EacFormat.CONCERT],
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
      renderOffer(offerProps)

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()
      const redactorName = screen.getByText('Jean Dupont')
      expect(redactorName).toBeInTheDocument()

      // First summary line
      expect(screen.getByText('Concert')).toBeInTheDocument()

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
      renderOffer({ ...offerProps, offer: offerInCayenne })

      const offerName = await screen.findByText(offerInCayenne.name)
      expect(offerName).toBeInTheDocument()

      expect(screen.getByText('Concert')).toBeInTheDocument()

      expect(screen.getByText('A la mairie')).toBeInTheDocument()

      expect(screen.getByText('26/09/2021 à 00:00')).toBeInTheDocument()
      expect(
        screen.queryByText('Jusqu’à', { exact: false })
      ).not.toBeInTheDocument()
      expect(screen.getByText('Gratuit')).toBeInTheDocument()
      expect(screen.getByText('Collège - 4e')).toBeInTheDocument()

      const seeMoreButton = await screen.findByRole('button', {
        name: 'en savoir plus',
      })
      await userEvent.click(seeMoreButton)

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

    it('should format the description when links are present and FF is on', async () => {
      renderOffer(
        {
          ...offerProps,
          offer: {
            ...offerInParis,
            description: `lien 1 : www.lien1.com
          https://lien2.com et https://lien3.com
          https://\nurl.com https://unlien avecuneespace
          contact: toto@toto.com`,
          },
        },
        user,
        {
          features: ['WIP_ENABLE_OFFER_MARKDOWN_DESCRIPTION'],
        }
      )

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()

      const descriptionParagraph = await screen.findByText('lien 1', {
        exact: false,
        selector: 'span',
      })

      const links = within(descriptionParagraph).getAllByRole('link')

      expect(links).toHaveLength(5)
      expect((links[0] as HTMLLinkElement).href).toBe('https://www.lien1.com/')
      expect((links[0] as HTMLLinkElement).childNodes[0].nodeValue).toBe(
        'www.lien1.com'
      )
      expect((links[1] as HTMLLinkElement).href).toBe('https://lien2.com/')
      expect((links[2] as HTMLLinkElement).href).toBe('https://lien3.com/')
      expect((links[3] as HTMLLinkElement).href).toBe('https://unlien/')
      expect((links[4] as HTMLLinkElement).href).toBe('mailto:toto@toto.com')
    })

    it('should display request form modal', async () => {
      renderOffer({
        ...offerProps,
        offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
      })

      const contactButton = screen.getByRole('button', {
        name: 'Contacter',
      })
      await userEvent.click(contactButton)

      expect(screen.getByText('Contacter le partenaire culturel'))
    })
  })

  it('should not display the distance to venue if the user does not have a valid geoloc', () => {
    user.lat = null
    user.lon = null
    renderOffer({
      ...offerProps,
    })

    expect(
      screen.queryByText('km de votre établissement')
    ).not.toBeInTheDocument()
  })

  it('should display the add to favorite button on offers that are not favorite yet', () => {
    renderOffer({
      ...offerProps,
      offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
    })

    expect(screen.getByText('Enregistrer en favoris')).toBeInTheDocument()
  })

  it('should display the remove from favorite button on offers that are already favorite', () => {
    renderOffer({
      ...offerProps,
      offer: {
        ...defaultCollectiveTemplateOffer,
        isFavorite: true,
        isTemplate: true,
      },
    })

    expect(screen.getByText('Supprimer des favoris')).toBeInTheDocument()
  })

  it("should toggle the favorite status of an offer when it's clicked", async () => {
    vi.spyOn(apiAdage, 'postCollectiveOfferFavorites').mockResolvedValue()
    vi.spyOn(apiAdage, 'deleteFavoriteForCollectiveOffer').mockResolvedValue()

    renderOffer({
      ...offerProps,
      offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
    })

    const toFavoriteButton = screen.getByRole('button', {
      name: 'Enregistrer en favoris',
    })

    await userEvent.click(toFavoriteButton)

    expect(screen.getByText('Supprimer des favoris')).toBeInTheDocument()

    const fromFavoriteButton = screen.getByRole('button', {
      name: 'Supprimer des favoris',
    })

    await userEvent.click(fromFavoriteButton)

    expect(screen.getByText('Enregistrer en favoris')).toBeInTheDocument()
  })

  it("should toggle the favorite status of a template offer when it's clicked", async () => {
    vi.spyOn(apiAdage, 'postCollectiveTemplateFavorites').mockResolvedValue()
    vi.spyOn(
      apiAdage,
      'deleteFavoriteForCollectiveOfferTemplate'
    ).mockResolvedValue()

    renderOffer({
      ...offerProps,
      offer: {
        ...offerProps.offer,
        dates: { end: '', start: '' },
        isTemplate: true,
      },
      afterFavoriteChange: () => {},
    })

    const toFavoriteButton = screen.getByRole('button', {
      name: 'Enregistrer en favoris',
    })

    await userEvent.click(toFavoriteButton)

    expect(screen.getByText('Supprimer des favoris')).toBeInTheDocument()

    const fromFavoriteButton = screen.getByRole('button', {
      name: 'Supprimer des favoris',
    })

    await userEvent.click(fromFavoriteButton)

    expect(screen.getByText('Enregistrer en favoris')).toBeInTheDocument()
  })

  it('should not change favorite status when set to favorite request fails', async () => {
    vi.spyOn(apiAdage, 'postCollectiveTemplateFavorites').mockRejectedValue(
      null
    )

    renderOffer({
      ...offerProps,
      offer: {
        ...defaultCollectiveTemplateOffer,
        isTemplate: true,
      },
    })

    const toFavoriteButton = screen.getByRole('button', {
      name: 'Enregistrer en favoris',
    })

    await userEvent.click(toFavoriteButton)

    expect(screen.getByText('Enregistrer en favoris')).toBeInTheDocument()
  })

  it('should not change favorite status when remove from favorite request fails', async () => {
    vi.spyOn(
      apiAdage,
      'deleteFavoriteForCollectiveOfferTemplate'
    ).mockRejectedValue(null)

    renderOffer({
      ...offerProps,
      offer: {
        ...defaultCollectiveTemplateOffer,
        isFavorite: true,
        isTemplate: true,
      },
    })

    const toFavoriteButton = screen.getByRole('button', {
      name: 'Supprimer des favoris',
    })

    await userEvent.click(toFavoriteButton)

    expect(screen.getByText('Supprimer des favoris')).toBeInTheDocument()
  })

  it('should not display favorite button when adage user is admin', () => {
    renderOffer(
      {
        ...offerProps,
        offer: {
          ...defaultCollectiveTemplateOffer,
          isTemplate: true,
        },
      },
      { ...user, role: AdageFrontRoles.READONLY }
    )

    expect(screen.queryByText('Enregistrer en favoris')).not.toBeInTheDocument()
  })

  it('should not display favorite button when offer is bookable', () => {
    renderOffer({
      ...offerProps,
    })

    expect(screen.queryByText('Enregistrer en favoris')).not.toBeInTheDocument()
  })

  it('should log event when clicking on "en savoir plus" button', async () => {
    renderOffer({
      ...offerProps,
      isInSuggestions: false,
      offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
    })

    const seeMoreButton = await screen.findByRole('button', {
      name: 'en savoir plus',
    })
    await userEvent.click(seeMoreButton)

    expect(apiAdage.logOfferTemplateDetailsButtonClick).toHaveBeenCalledWith({
      iframeFrom: '/',
      isFromNoResult: false,
      queryId: '1',
      offerId: 1,
    })
  })

  it('should mention if the log is from a suggestion offer when clicking on "en savoir plus" button', async () => {
    renderOffer({ ...offerProps, isInSuggestions: true })

    const seeMoreButton = await screen.findByRole('button', {
      name: 'en savoir plus',
    })
    await userEvent.click(seeMoreButton)

    expect(apiAdage.logOfferDetailsButtonClick).toHaveBeenCalledWith({
      iframeFrom: '/',
      isFromNoResult: true,
      queryId: '1',
      stockId: 825,
    })
  })

  it('should display format', () => {
    renderOffer(
      {
        ...offerProps,
        offer: {
          ...defaultCollectiveTemplateOffer,
          isTemplate: true,
          formats: [EacFormat.CONCERT, EacFormat.REPR_SENTATION],
        },
      },
      user
    )

    expect(screen.getByText('Concert, Représentation')).toBeInTheDocument()
  })

  it('should display a link as the name of the venue when the venue has a valid adageId', () => {
    renderOffer({
      ...offerProps,
      offer: {
        ...offerProps.offer,
        venue: { ...offerProps.offer.venue, adageId: '123' },
      },
    })

    expect(
      screen.getByRole('link', {
        name: 'Le Petit Rintintin 33 - Le Petit Rintintin Management (75000)',
      })
    ).toBeInTheDocument()
  })

  it('should not display a link as the name of the venue when the venue has no valid adageId', () => {
    renderOffer(offerProps)

    expect(
      screen.queryByRole('link', {
        name: 'Le Petit Rintintin 33 - Le Petit Rintintin Management (75000)',
      })
    ).not.toBeInTheDocument()
  })

  it('should trigger a tracking event when the venue name link is clicked', async () => {
    renderOffer({
      ...offerProps,
      offer: {
        ...offerProps.offer,
        venue: { ...offerProps.offer.venue, adageId: '123' },
      },
    })

    const link = screen.getByRole('link', {
      name: 'Le Petit Rintintin 33 - Le Petit Rintintin Management (75000)',
    })

    await userEvent.click(link)

    expect(apiAdage.logTrackingMap).toHaveBeenCalled()
  })

  it('should not display share link when offer is not template', () => {
    renderOffer(
      {
        ...offerProps,
        offer: {
          ...offerInParis,
        },
      },
      { ...user, role: AdageFrontRoles.READONLY }
    )

    expect(
      screen.queryByText('Partager l’offre par email')
    ).not.toBeInTheDocument()
  })

  it('should show the redirect button instead of the expand button when the ff is enabled', () => {
    renderOffer(
      {
        ...offerProps,
        offer: {
          ...defaultCollectiveTemplateOffer,
          isTemplate: true,
        },
      },
      undefined,
      {
        features: ['WIP_ENABLE_NEW_ADAGE_OFFER_DESIGN'],
      }
    )

    expect(
      screen.queryByRole('button', { name: 'en savoir plus' })
    ).not.toBeInTheDocument()

    const redirectLink = screen.getByRole('link', {
      name: 'Nouvelle fenêtre Découvrir l’offre',
    })

    expect(redirectLink).toBeInTheDocument()

    expect(redirectLink.getAttribute('href')).toContain(
      `offerid/${defaultCollectiveTemplateOffer.id}`
    )
  })

  it('should redirect to the bookable offer url with the "B-" when the offer is bookable', () => {
    renderOffer(offerProps, undefined, {
      features: ['WIP_ENABLE_NEW_ADAGE_OFFER_DESIGN'],
    })

    const redirectLink = screen.getByRole('link', {
      name: 'Nouvelle fenêtre Découvrir l’offre',
    })

    expect(redirectLink.getAttribute('href')).toContain(
      `offerid/B-${offerProps.offer.id}`
    )
  })

  it('should not display contact button when FF is active', () => {
    renderOffer(
      {
        ...offerProps,
        offer: {
          ...defaultCollectiveTemplateOffer,
          isTemplate: true,
        },
      },
      user,
      { features: ['WIP_ENABLE_NEW_ADAGE_OFFER_DESIGN'] }
    )

    expect(screen.queryByText('Contacter')).not.toBeInTheDocument()
  })
})
