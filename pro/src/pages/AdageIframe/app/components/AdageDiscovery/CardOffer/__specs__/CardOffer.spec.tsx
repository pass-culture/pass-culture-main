import { render, screen } from '@testing-library/react'

import { OfferAddressType } from 'apiClient/adage'
import { defaultCollectiveOffer } from 'utils/adageFactories'

import CardOfferComponent, {
  CardComponentProps,
  CardOfferModel,
} from '../CardOffer'

const mockOffer: CardOfferModel = {
  ...defaultCollectiveOffer,
  venue: {
    ...defaultCollectiveOffer.venue,
    distance: 5,
  },
  offerVenue: {
    ...defaultCollectiveOffer.offerVenue,
    distance: 10,
  },
  isTemplate: false,
}

const renderCardOfferComponent = ({ offer }: CardComponentProps) => {
  render(<CardOfferComponent offer={offer} />)
}

describe('CardOffer component', () => {
  it('should render school tag when offer will happens in school', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.SCHOOL,
      },
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('En classe')).toBeInTheDocument()
  })

  it('should render offer venue tag when offer will happens in pro venue', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
      },
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('Sortie')).toBeInTheDocument()
    expect(screen.getByText('À 10 km')).toBeInTheDocument()
  })

  it('should render other venue tag when offer will happens in other venue than pro one', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.OTHER,
      },
    }
    renderCardOfferComponent({ offer })

    expect(screen.getByText('Sortie')).toBeInTheDocument()
    expect(screen.getByText('Lieu à définir')).toBeInTheDocument()
  })
})
