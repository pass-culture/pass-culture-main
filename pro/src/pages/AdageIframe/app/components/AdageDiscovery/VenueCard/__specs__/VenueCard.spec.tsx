import { screen } from '@testing-library/react'
import * as router from 'react-router-dom'

import { LocalOfferersPlaylistOffer } from 'apiClient/adage'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueCard, VenueCardProps } from '../VenueCard'

const mockVenue: LocalOfferersPlaylistOffer = {
  imgUrl: 'testImageUrl.com',
  name: 'Le nom administratif du lieu',
  publicName: 'Mon super lieu',
  distance: 2,
  id: 28,
  city: 'Paris',
}

const renderVenueCard = ({
  venue,
  handlePlaylistElementTracking,
}: VenueCardProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <VenueCard
        venue={venue}
        handlePlaylistElementTracking={handlePlaylistElementTracking}
      />
    </AdageUserContextProvider>
  )
}

describe('VenueCard', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useSearchParams').mockReturnValueOnce([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])
  })

  it('should display venue name if publicName is not defined', () => {
    renderVenueCard({
      venue: { ...mockVenue, publicName: undefined },
      handlePlaylistElementTracking: vi.fn(),
    })

    expect(screen.getByText(mockVenue.name)).toBeInTheDocument()
  })

  it('should redirect on click in offer card', () => {
    renderVenueCard({
      venue: mockVenue,
      handlePlaylistElementTracking: vi.fn(),
    })

    const offerElement = screen.getByTestId('card-venue-link')

    expect(offerElement).toHaveAttribute(
      'href',
      '/adage-iframe/recherche?token=123&venue=28'
    )
  })
})
