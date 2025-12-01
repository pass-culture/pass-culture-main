import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import * as useIsElementVisible from '@/commons/hooks/useIsElementVisible'
import * as useNotification from '@/commons/hooks/useNotification'
import { defaultCollectiveOffer } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { ClassroomPlaylist } from './ClassroomPlaylist'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
    getClassroomPlaylist: vi.fn(),
  },
}))

const mockTrackPlaylistElementClicked = vi.fn()
const mockOnWholePlaylistSeen = vi.fn()

const renderClassroomPlaylist = () => {
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <ClassroomPlaylist
        onWholePlaylistSeen={mockOnWholePlaylistSeen}
        trackPlaylistElementClicked={mockTrackPlaylistElementClicked}
      />
    </AdageUserContextProvider>
  )
}

describe('AdageDiscover classRoomPlaylist', () => {
  const notifyError = vi.fn()

  beforeEach(async () => {
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')
    vi.spyOn(apiAdage, 'getClassroomPlaylist').mockResolvedValue({
      collectiveOffers: [defaultCollectiveOffer],
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

  it('should render new offer playlist', async () => {
    renderClassroomPlaylist()

    expect(
      await screen.findByText(
        'Ces interventions peuvent avoir lieu dans votre établissement'
      )
    ).toBeInTheDocument()
  })

  it('should call tracker for classroom playlist element', async () => {
    renderClassroomPlaylist()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const classRoomPlaylistElement = screen.getByText('Une chouette à la mer')
    classRoomPlaylistElement.addEventListener('click', (e) => {
      e.preventDefault()
    })
    await userEvent.click(classRoomPlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenNthCalledWith(1, {
      index: 0,
      offerId: 479,
      playlistId: 2,
      playlistType: 'offer',
    })
  })

  it('should call tracker when whole classroom playlist is seen', async () => {
    renderClassroomPlaylist()
    vi.spyOn(useIsElementVisible, 'useIsElementVisible')
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(mockOnWholePlaylistSeen).toHaveBeenNthCalledWith(1, {
      playlistId: 2,
      playlistType: 'offer',
      numberOfTiles: 1,
    })
  })
})
