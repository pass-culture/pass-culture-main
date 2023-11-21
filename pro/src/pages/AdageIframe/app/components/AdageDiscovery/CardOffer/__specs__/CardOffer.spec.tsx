import { screen } from '@testing-library/react'
import * as router from 'react-router-dom'

import { OfferAddressType } from 'apiClient/adage'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser, defaultCollectiveOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

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
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <CardOfferComponent offer={offer} />
    </AdageUserContextProvider>
  )
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

  it('should redirect on click in offer card', () => {
    vi.spyOn(router, 'useSearchParams').mockReturnValue([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])

    renderCardOfferComponent({ offer: mockOffer })

    const offerElement = screen.getByTestId('card-offer-link')

    expect(offerElement).toHaveAttribute(
      'href',
      '/adage-iframe/decouverte/offre/479?token=123'
    )
  })
})
