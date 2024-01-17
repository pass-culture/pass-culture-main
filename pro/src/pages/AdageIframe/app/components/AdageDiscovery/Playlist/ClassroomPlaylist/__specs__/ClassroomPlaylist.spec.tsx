import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultCollectiveOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ClassroomPlaylist } from '../ClassroomPlaylist'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
    getClassroomPlaylist: vi.fn(),
  },
}))

const mockTrackPlaylistElementClicked = vi.fn()
const mockOnWholePlaylistSeen = vi.fn()

const renderNewOfferPlaylist = () => {
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
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.default>
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
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
    renderNewOfferPlaylist()

    expect(
      await screen.findByText(
        'Ces interventions peuvent avoir lieu dans votre classe'
      )
    ).toBeInTheDocument()
  })

  it('should show an error message notification when classroom offer could not be fetched', async () => {
    vi.spyOn(apiAdage, 'getClassroomPlaylist').mockRejectedValueOnce(null)

    renderNewOfferPlaylist()
    await waitFor(() =>
      expect(apiAdage.getClassroomPlaylist).toHaveBeenCalled()
    )

    expect(notifyError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
  })

  it('should call tracker for classroom playlist element', async () => {
    renderNewOfferPlaylist()

    await waitForElementToBeRemoved(() =>
      screen.queryAllByText(/Chargement en cours/)
    )

    const classRoomPlaylistElement = screen.getByText('Une chouette à la mer')

    await userEvent.click(classRoomPlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenCalledTimes(1)
  })
})
