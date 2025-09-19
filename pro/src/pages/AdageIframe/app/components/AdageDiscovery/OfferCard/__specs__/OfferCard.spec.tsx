import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import {
  type AuthenticatedResponse,
  CollectiveLocationType,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { type CardComponentProps, OfferCardComponent } from '../OfferCard'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
  },
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

const mockOffer = {
  ...defaultCollectiveOffer,
  venue: {
    ...defaultCollectiveOffer.venue,
    distance: 5,
  },
  isTemplate: false,
}

const adageUser: AuthenticatedResponse = {
  ...defaultAdageUser,
  lat: 48.86543326111946,
  lon: 2.321135886028998,
}

const renderOfferCardComponent = (
  { offer, onCardClicked }: CardComponentProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <OfferCardComponent offer={offer} onCardClicked={onCardClicked} />
    </AdageUserContextProvider>,
    options
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

  it('should render location tag when offer has location attribute', () => {
    const offer = {
      ...mockOffer,
      location: {
        locationType: CollectiveLocationType.SCHOOL,
      },
    }
    renderOfferCardComponent({ offer, onCardClicked: vi.fn() })

    expect(
      screen.getByText(/Dans l’établissement scolaire/)
    ).toBeInTheDocument()
  })
})
