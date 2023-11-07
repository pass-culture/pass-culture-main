import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import CardVenue, { CardVenueProps } from '../CardVenue'

const mockVenue = {
  imageUrl: 'testImageUrl.com',
  name: 'Le nom administratif du lieu',
  publicName: 'Mon super lieu',
  distance: 2,
  id: '28',
  city: 'Paris',
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useNavigate: vi.fn(),
}))

const renderCardVenue = ({ venue }: CardVenueProps) => {
  render(<CardVenue venue={venue} />)
}

describe('CardVenue', () => {
  it('should display venue name if publicName is not defined', () => {
    renderCardVenue({ venue: { ...mockVenue, publicName: undefined } })

    expect(screen.getByText(mockVenue.name)).toBeInTheDocument()
  })

  it('should navigate to search with venue filter when clicking the card', async () => {
    const mockNavigate = vi.fn()
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    renderCardVenue({ venue: mockVenue })

    await userEvent.click(screen.getByText(mockVenue.publicName))

    expect(mockNavigate).toHaveBeenCalledWith(
      '/adage-iframe/venue/28?token=null'
    )
  })
})
