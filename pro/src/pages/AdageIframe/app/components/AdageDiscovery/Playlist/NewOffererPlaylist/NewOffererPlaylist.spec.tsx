import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import type { LocalOfferersPlaylistOffer } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import * as useIsElementVisible from '@/commons/hooks/useIsElementVisible'
import * as useNotification from '@/commons/hooks/useNotification'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NewOffererPlaylist } from './NewOffererPlaylist'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
    getNewOfferersPlaylist: vi.fn(),
  },
}))

const mockTrackPlaylistElementClicked = vi.fn()
const mockOnWholePlaylistSeen = vi.fn()

const mockNewOffererPlaylist: LocalOfferersPlaylistOffer = {
  city: 'Paris',
  distance: 5,
  id: 1,
  imgUrl: 'mock',
  name: 'venuePlaylist offer 1',
  publicName: 'Venue playlist offer 1',
}

const renderNewOffererPlaylist = () => {
  renderWithProviders(
    <NewOffererPlaylist
      onWholePlaylistSeen={mockOnWholePlaylistSeen}
      trackPlaylistElementClicked={mockTrackPlaylistElementClicked}
    />
  )
}

describe('NewOffererPlaylist', () => {
  const notifyError = vi.fn()

  beforeEach(async () => {
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')
    vi.spyOn(apiAdage, 'getNewOfferersPlaylist').mockResolvedValue({
      venues: [mockNewOffererPlaylist],
    })

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
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

  it('should render new offerer playlist', async () => {
    renderNewOffererPlaylist()

    expect(
      await screen.findByText(
        'Ces partenaires culturels ont été récemment référencés'
      )
    ).toBeInTheDocument()
  })

  it('should call tracker for venue playlist element', async () => {
    renderNewOffererPlaylist()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const venuePlaylistElement = await screen.findByText(
      'Venue playlist offer 1'
    )

    await userEvent.click(venuePlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenNthCalledWith(1, {
      index: 0,
      venueId: 1,
      playlistId: 4,
      playlistType: 'venue',
    })
  })

  it('should call tracker when whole venue playlist is seen', async () => {
    renderNewOffererPlaylist()
    vi.spyOn(useIsElementVisible, 'useIsElementVisible')
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(mockOnWholePlaylistSeen).toHaveBeenNthCalledWith(1, {
      playlistId: 4,
      playlistType: 'venue',
      numberOfTiles: 1,
    })
  })
})
