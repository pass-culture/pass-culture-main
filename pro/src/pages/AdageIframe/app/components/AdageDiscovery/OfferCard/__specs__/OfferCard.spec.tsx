import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { AuthenticatedResponse, OfferAddressType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CardComponentProps, OfferCardComponent } from '../OfferCard'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
  },
}))

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useLocation: vi.fn(),
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
  onCardClicked,
}: CardComponentProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <OfferCardComponent offer={offer} onCardClicked={onCardClicked} />
    </AdageUserContextProvider>
  )
}

const defaultUseLocationValue = {
  state: { offer: defaultCollectiveTemplateOffer },
  hash: '',
  key: '',
  pathname: '/adage-iframe/decouverte/offre/10',
  search: '',
}

describe('OfferCard component', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)
  })

  it('should render school tag when offer will happens in school', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.SCHOOL,
      },
    }
    renderOfferCardComponent({ offer, onCardClicked: vi.fn() })

    expect(
      screen.getByText(/Dans l’établissement scolaire/)
    ).toBeInTheDocument()
  })

  it('should render offer venue tag when offer will happens in pro venue', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
      },
    }
    renderOfferCardComponent({ offer, onCardClicked: vi.fn() })

    expect(screen.getByText(/Sortie/)).toBeInTheDocument()
    expect(screen.getByText(/À 10 km/)).toBeInTheDocument()
  })

  it('should render other venue tag when offer will happens in other venue than pro one', () => {
    const offer = {
      ...mockOffer,
      offerVenue: {
        ...mockOffer.offerVenue,
        addressType: OfferAddressType.OTHER,
      },
    }
    renderOfferCardComponent({ offer, onCardClicked: vi.fn() })

    expect(screen.getByText(/Sortie/)).toBeInTheDocument()
    expect(screen.getByText(/Lieu à définir/)).toBeInTheDocument()
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
    renderOfferCardComponent({ offer, onCardClicked: vi.fn() })

    expect(screen.getByText('à 1 km - Paris')).toBeInTheDocument()
  })

  it('should redirect with "découverte" in url on click in offer card', () => {
    vi.spyOn(router, 'useSearchParams').mockReturnValueOnce([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])

    renderOfferCardComponent({
      offer: mockOffer,
      onCardClicked: vi.fn(),
    })

    const offerElement = screen.getByTestId('card-offer-link')

    expect(offerElement).toHaveAttribute(
      'href',
      '/adage-iframe/decouverte/offre/479?token=123'
    )
  })

  it('should redirect with "recherche" in url on click in offer card', () => {
    vi.spyOn(router, 'useSearchParams').mockReturnValueOnce([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      pathname: '/adage-iframe/recherche/offre/479',
    })

    renderOfferCardComponent({
      offer: mockOffer,
      onCardClicked: vi.fn(),
    })

    const offerElement = screen.getByTestId('card-offer-link')

    expect(offerElement).toHaveAttribute(
      'href',
      '/adage-iframe/recherche/offre/479?token=123'
    )
  })

  it('should call tracking route on click in offer card', async () => {
    const mockHandleTracking = vi.fn()
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')

    renderOfferCardComponent({
      offer: mockOffer,
      onCardClicked: mockHandleTracking,
    })

    const offerElement = screen.getByTestId('card-offer-link')

    offerElement.setAttribute('href', '')

    await userEvent.click(offerElement)

    expect(mockHandleTracking).toHaveBeenCalledTimes(1)
  })
})
