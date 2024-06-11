import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  EacFormat,
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

  let offerProps: OfferProps
  beforeEach(() => {
    offerInParis = { ...defaultCollectiveOffer, isTemplate: false }

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

  it('should redirect to the bookable offer url with the "B-" when the offer is bookable', () => {
    renderOffer(offerProps, undefined)

    const redirectLink = screen.getByRole('link', {
      name: 'Nouvelle fenêtre Découvrir l’offre',
    })

    expect(redirectLink.getAttribute('href')).toContain(
      `offerid/B-${offerProps.offer.id}`
    )
  })
})
