import { screen } from '@testing-library/react'

import { AdageFrontRoles, StudentLevels } from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AdageOfferProps } from '../../AdageOffer'
import { AdageOfferHeader } from '../AdageOfferHeader'

function renderAdageOfferHeader(
  props: AdageOfferProps = {
    offer: defaultCollectiveTemplateOffer,
    adageUser: defaultAdageUser,
    isPreview: false,
  }
) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
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

  it("should show the offer title even if it's a preview of the offer", () => {
    renderAdageOfferHeader({
      offer: defaultCollectiveTemplateOffer,
      adageUser: defaultAdageUser,
      isPreview: true,
    })

    expect(
      screen.getByText(defaultCollectiveTemplateOffer.name)
    ).toBeInTheDocument()
  })

  it('should show the offer image if it has one', () => {
    renderAdageOfferHeader({
      offer: { ...defaultCollectiveTemplateOffer, imageUrl: 'test_url' },
      adageUser: defaultAdageUser,
    })

    expect(screen.getByRole('presentation')).toHaveAttribute('src', 'test_url')
  })

  it('should not show an image if the offer has no image', () => {
    renderAdageOfferHeader({
      offer: { ...defaultCollectiveTemplateOffer, imageUrl: undefined },
      adageUser: defaultAdageUser,
    })

    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })

  it('should show the action buttons if the offer is template', () => {
    renderAdageOfferHeader()

    expect(
      screen.getByRole('button', { name: 'Mettre en favoris' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Partager par email' })
    ).toBeInTheDocument()
  })

  it('should not show the action buttons if the offer is bookable', () => {
    renderAdageOfferHeader({
      offer: defaultCollectiveOffer,
      adageUser: defaultAdageUser,
    })

    expect(
      screen.queryByRole('button', { name: 'Mettre en favoris' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', { name: 'Partager par email' })
    ).not.toBeInTheDocument()
  })

  it('should not show the favorite button if the user is not admin', () => {
    renderAdageOfferHeader({
      offer: defaultCollectiveTemplateOffer,
      adageUser: { ...defaultAdageUser, role: AdageFrontRoles.READONLY },
    })

    expect(
      screen.queryByRole('button', { name: 'Mettre en favoris' })
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
      adageUser: defaultAdageUser,
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
      adageUser: defaultAdageUser,
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
      adageUser: defaultAdageUser,
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
          end: '2024-01-29T20:00:28.040559Z',
          start: '2024-01-23T20:00:28.040547Z',
        },
      },
      adageUser: defaultAdageUser,
    })

    expect(
      screen.getByText('Du 23 janvier au 29 janvier 2024 à 20h')
    ).toBeInTheDocument()
  })

  it('should show that the offer is permanent if it has no dates', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        dates: undefined,
      },
      adageUser: defaultAdageUser,
    })

    expect(
      screen.getByText(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    ).toBeInTheDocument()
  })

  it('should show "Multiniveaux" instead of the list of student levels when there are more than 1', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveTemplateOffer,
        students: [StudentLevels.CAP_1RE_ANN_E, StudentLevels.COLL_GE_3E],
      },
      adageUser: defaultAdageUser,
    })

    expect(screen.getByText('Multiniveaux')).toBeInTheDocument()
  })

  it('should show the institution and the price if the offer is bookable', () => {
    renderAdageOfferHeader({
      offer: {
        ...defaultCollectiveOffer,
        educationalInstitution: {
          name: 'My institution',
          city: 'Paris',
          postalCode: '75000',
          id: 1,
        },
        stock: {
          ...defaultCollectiveOffer.stock,
          numberOfTickets: 100,
          price: 12000,
        },
      },
      adageUser: defaultAdageUser,
    })

    expect(screen.getByText('120 € pour 100 participants')).toBeInTheDocument()
    expect(screen.getByText(/My institution/)).toBeInTheDocument()
  })
})
