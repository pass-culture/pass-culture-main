import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { AuthenticatedResponse, OfferAddressType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser, defaultCollectiveOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferCardComponent, { CardComponentProps } from '../OfferCard'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
  },
}))

const mockOffer = {
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

const adageUser: AuthenticatedResponse = {
  ...defaultAdageUser,
  lat: 48.86543326111946,
  lon: 2.321135886028998,
}

const renderOfferCardComponent = ({
  offer,
  handlePlaylistElementTracking,
}: CardComponentProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <OfferCardComponent
        offer={offer}
        handlePlaylistElementTracking={handlePlaylistElementTracking}
      />
    </AdageUserContextProvider>
  )
}

describe('OfferCard component', () => {
  it('should render school tag when offer will happens in school', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.SCHOOL,
      },
    }
    renderOfferCardComponent({ offer, handlePlaylistElementTracking: vi.fn() })

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
    renderOfferCardComponent({ offer, handlePlaylistElementTracking: vi.fn() })

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
    renderOfferCardComponent({ offer, handlePlaylistElementTracking: vi.fn() })

    expect(screen.getByText('Sortie')).toBeInTheDocument()
    expect(screen.getByText('Lieu à définir')).toBeInTheDocument()
  })

  it('should display the distance when it is available', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
      },
      venue: {
        ...mockOffer.venue,
        coordinates: {
          latitude: 48.869440910282734,
          longitude: 2.3087717501609233,
        },
      },
    }
    renderOfferCardComponent({ offer, handlePlaylistElementTracking: vi.fn() })

    expect(screen.getByText('à 1 km - Paris')).toBeInTheDocument()
  })

  it('should redirect on click in offer card', () => {
    vi.spyOn(router, 'useSearchParams').mockReturnValueOnce([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])

    renderOfferCardComponent({
      offer: mockOffer,
      handlePlaylistElementTracking: vi.fn(),
    })

    const offerElement = screen.getByTestId('card-offer-link')

    expect(offerElement).toHaveAttribute(
      'href',
      '/adage-iframe/decouverte/offre/479?token=123'
    )
  })

  it('should call tracking route on click in offer card', async () => {
    const mockhandlePlaylistElementTracking = vi.fn()
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')

    renderOfferCardComponent({
      offer: mockOffer,
      handlePlaylistElementTracking: mockhandlePlaylistElementTracking,
    })

    const offerElement = screen.getByTestId('card-offer-link')

    offerElement.setAttribute('href', '')

    await userEvent.click(offerElement)

    expect(mockhandlePlaylistElementTracking).toHaveBeenCalledTimes(1)
  })
})
