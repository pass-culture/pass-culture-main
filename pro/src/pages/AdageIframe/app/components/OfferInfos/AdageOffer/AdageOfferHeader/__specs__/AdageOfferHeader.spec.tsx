import { screen } from '@testing-library/react'

import { AdageFrontRoles } from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import AdageOfferHeader, { AdageOfferProps } from '../AdageOfferHeader'

function renderAdageOfferHeader(
  props: AdageOfferProps = { offer: defaultCollectiveTemplateOffer },
  user = defaultAdageUser
) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <AdageOfferHeader {...props} />
    </AdageUserContextProvider>
  )
}

describe('AdageOfferHeader', () => {
  it('should show the offer title', () => {
    renderAdageOfferHeader()

    expect(
      screen.getByText(defaultCollectiveTemplateOffer.name)
    ).toBeInTheDocument()
  })

  it('should show the offer image if it has one', () => {
    renderAdageOfferHeader({
      offer: { ...defaultCollectiveTemplateOffer, imageUrl: 'test_url' },
    })

    expect(screen.getByRole('img')).toHaveAttribute('src', 'test_url')
  })

  it('should not show an image if the offer has no image', () => {
    renderAdageOfferHeader({
      offer: { ...defaultCollectiveTemplateOffer, imageUrl: undefined },
    })

    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })

  it('should show the action buttons if the offer is template', () => {
    renderAdageOfferHeader()

    expect(
      screen.getByRole('button', { name: 'Enregistrer en favoris' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Partager l’offre par email' })
    ).toBeInTheDocument()
  })

  it('should not show the action buttons if the offer is bookable', () => {
    renderAdageOfferHeader({ offer: defaultCollectiveOffer })

    expect(
      screen.queryByRole('button', { name: 'Enregistrer en favoris' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', { name: 'Partager l’offre par email' })
    ).not.toBeInTheDocument()
  })

  it('should not show the favorite button if the user is not admin', () => {
    renderAdageOfferHeader(
      { offer: defaultCollectiveTemplateOffer },
      { ...defaultAdageUser, role: AdageFrontRoles.READONLY }
    )

    expect(
      screen.queryByRole('button', { name: 'Enregistrer en favoris' })
    ).not.toBeInTheDocument()
  })

  it("should show the offer's venue name", () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: {
          ...defaultCollectiveTemplateOffer.venue,
          publicName: 'Test venue name',
          postalCode: '33333',
          city: 'Ville test',
        },
      },
    })

    expect(screen.getByText(/Test venue name/)).toBeInTheDocument()
    expect(screen.getByText(/33333, Ville test/)).toBeInTheDocument()
  })

  it('should show that the offer happens in school', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        offerVenue: {
          ...defaultCollectiveTemplateOffer.offerVenue,
          addressType: OfferAddressType.SCHOOL,
        },
      },
    })

    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should show that the offer happens at a specific address', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        offerVenue: {
          ...defaultCollectiveTemplateOffer.offerVenue,
          addressType: OfferAddressType.OTHER,
          otherAddress: '123 this is a very specific address',
        },
      },
    })

    expect(
      screen.getByText('123 this is a very specific address')
    ).toBeInTheDocument()
  })

  it('should show the dates of a template offer that has specific dates', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        dates: {
          end: '2024-01-29T23:00:28.040559Z',
          start: '2024-01-23T23:00:28.040547Z',
        },
      },
    })

    expect(
      screen.getByText('Du 23 janvier au 29 janvier 2024 à 23h')
    ).toBeInTheDocument()
  })

  it('should show that the offer is permanent if it has no dates', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        dates: undefined,
      },
    })

    expect(
      screen.getByText(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    ).toBeInTheDocument()
  })
})
