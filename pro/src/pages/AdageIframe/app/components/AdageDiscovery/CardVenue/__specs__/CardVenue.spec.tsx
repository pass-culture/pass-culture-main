import { screen } from '@testing-library/react'
import * as router from 'react-router-dom'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CardVenue, { CardVenueProps } from '../CardVenue'

const mockVenue = {
  imageUrl: 'testImageUrl.com',
  name: 'Le nom administratif du lieu',
  publicName: 'Mon super lieu',
  distance: 2,
  id: '28',
  city: 'Paris',
}

const renderCardVenue = ({
  venue,
  handlePlaylistElementTracking,
}: CardVenueProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <CardVenue
        venue={venue}
        handlePlaylistElementTracking={handlePlaylistElementTracking}
      />
    </AdageUserContextProvider>
  )
}

describe('CardVenue', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useSearchParams').mockReturnValueOnce([
      new URLSearchParams({ token: '123' }),
      vi.fn(),
    ])
  })

  it('should display venue name if publicName is not defined', () => {
    renderCardVenue({
      venue: { ...mockVenue, publicName: undefined },
      handlePlaylistElementTracking: vi.fn(),
    })

    expect(screen.getByText(mockVenue.name)).toBeInTheDocument()
  })

  it('should redirect on click in offer card', () => {
    renderCardVenue({
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
