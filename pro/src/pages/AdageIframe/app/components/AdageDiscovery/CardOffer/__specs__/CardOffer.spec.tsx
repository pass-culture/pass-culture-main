import { render, screen } from '@testing-library/react'

import { OfferAddressType } from 'apiClient/adage'

import CardOfferComponent, { CardComponentProps } from '../CardOffer'

const mockOffer = {
  imageUrl: 'https://picsum.photos/200/300',
  name: 'Titre de l’offre maximum sur 3 lignes. Passé ces trois lignes, il faut tronquer le texte',
  offerAddressType: OfferAddressType.OTHER,
  venue: {
    name: 'Venue 1',
    distance: 5,
    city: 'Paris',
  },
  offerVenue: {
    name: 'Venue 2',
    distance: 10,
    city: 'Paris',
  },
}

const renderCardOfferComponent = ({ offer }: CardComponentProps) => {
  render(<CardOfferComponent offer={offer} />)
}

describe('CardOffer component', () => {
  it('should render school tag when offer will happens in school', () => {
    const offer = {
      ...mockOffer,
      offerAddressType: OfferAddressType.SCHOOL,
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('En classe')).toBeInTheDocument()
  })

  it('should render offer venue tag when offer will happens in pro venue', () => {
    const offer = {
      ...mockOffer,
      offerAddressType: OfferAddressType.OFFERER_VENUE,
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('Sortie')).toBeInTheDocument()
    expect(screen.getByText('À 10 km')).toBeInTheDocument()
  })

  it('should render other venue tag when offer will happens in other venue than pro one', () => {
    const offer = {
      ...mockOffer,
      offerAddressType: OfferAddressType.OTHER,
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('Sortie')).toBeInTheDocument()
    expect(screen.getByText('Lieu à définir')).toBeInTheDocument()
  })
})
