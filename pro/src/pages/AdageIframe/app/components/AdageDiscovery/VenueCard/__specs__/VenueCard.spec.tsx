import { screen } from '@testing-library/react'
import * as router from 'react-router'

import type { LocalOfferersPlaylistOffer } from '@/apiClient/adage'
import { defaultAdageUser } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { VenueCard, type VenueCardProps } from '../VenueCard'

const mockVenue: LocalOfferersPlaylistOffer = {
  imgUrl: 'testImageUrl.com',
  name: 'Le nom administratif du lieu',
  publicName: 'Mon super lieu',
  distance: 2,
  id: 28,
  city: 'Paris',
}

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useSearchParams: () => [],
}))

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
