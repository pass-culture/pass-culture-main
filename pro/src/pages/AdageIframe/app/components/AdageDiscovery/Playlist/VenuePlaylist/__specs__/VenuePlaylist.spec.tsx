import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { LocalOfferersPlaylistOffer } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenuePlaylist } from '../VenuePlaylist'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
    getLocalOfferersPlaylist: vi.fn(),
  },
}))

const mockTrackPlaylistElementClicked = vi.fn()
const mockOnWholePlaylistSeen = vi.fn()

const mockLocalOfferersPlaylistOffer: LocalOfferersPlaylistOffer = {
  city: 'Paris',
  distance: 5,
  id: 1,
  imgUrl: 'mock',
  name: 'venuePlaylist offer 1',
  publicName: 'Venue playlist offer 1',
}

const renderNewOfferPlaylist = () => {
  renderWithProviders(
    <VenuePlaylist
      onWholePlaylistSeen={mockOnWholePlaylistSeen}
      trackPlaylistElementClicked={mockTrackPlaylistElementClicked}
    />
  )
}

describe('VenuePlaylist', () => {
  const notifyError = vi.fn()

  beforeEach(async () => {
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')
    vi.spyOn(apiAdage, 'getLocalOfferersPlaylist').mockResolvedValue({
      venues: [mockLocalOfferersPlaylistOffer],
    })

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))
  })

  it('should render venue playlist', async () => {
    renderNewOfferPlaylist()

    expect(
      await screen.findByText(
        'À environ 30 minutes de transport de mon établissement'
      )
    ).toBeInTheDocument()
  })

  it('should call tracker for venue playlist element', async () => {
    renderNewOfferPlaylist()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const venuePlaylistElement = await screen.findByText(
      'Venue playlist offer 1'
    )

    await userEvent.click(venuePlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenCalledTimes(1)
  })

  it.each([
    {
      distance: 3,
      title: 'À moins de 30 minutes à pieds de mon établissement',
    },
    {
      distance: 15,
      title: 'À environ 30 minutes de transport de mon établissement',
    },
    {
      distance: 30,
      title: 'À environ 1h de transport de mon établissement',
    },
  ])(
    'should display the playlist title based on the maximum venue distance',
    async ({ distance, title }) => {
      vi.spyOn(apiAdage, 'getLocalOfferersPlaylist').mockResolvedValueOnce({
        venues: [{ ...mockLocalOfferersPlaylistOffer, distance }],
      })
      renderNewOfferPlaylist()

      expect(await screen.findByText(title)).toBeInTheDocument()
    }
  )
})
