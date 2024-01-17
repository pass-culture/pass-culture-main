import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  InstitutionRuralLevel,
  LocalOfferersPlaylistOffer,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
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

const renderNewOfferPlaylist = (user: AuthenticatedResponse) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <VenuePlaylist
        onWholePlaylistSeen={mockOnWholePlaylistSeen}
        trackPlaylistElementClicked={mockTrackPlaylistElementClicked}
      />
    </AdageUserContextProvider>
  )
}

describe('AdageDiscover classRoomPlaylist', () => {
  const notifyError = vi.fn()
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  beforeEach(async () => {
    vi.spyOn(apiAdage, 'logConsultPlaylistElement')
    vi.spyOn(apiAdage, 'getLocalOfferersPlaylist').mockResolvedValue({
      venues: [mockLocalOfferersPlaylistOffer],
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

  it('should render venue playlist', async () => {
    renderNewOfferPlaylist(user)

    expect(
      await screen.findByText(
        'À moins de 30 minutes à pied de mon établissement'
      )
    ).toBeInTheDocument()
  })

  it('should show an error message notification when venue could not be fetched', async () => {
    vi.spyOn(apiAdage, 'getLocalOfferersPlaylist').mockRejectedValueOnce(null)

    renderNewOfferPlaylist(user)
    await waitFor(() =>
      expect(apiAdage.getLocalOfferersPlaylist).toHaveBeenCalled()
    )

    expect(notifyError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
  })

  it('should call tracker for venue playlist element', async () => {
    renderNewOfferPlaylist(user)

    await waitForElementToBeRemoved(() =>
      screen.queryAllByText(/Chargement en cours/)
    )

    const venuePlaylistElement = await screen.findByText(
      'Venue playlist offer 1'
    )

    await userEvent.click(venuePlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenCalledTimes(1)
  })

  it.each([
    {
      level: InstitutionRuralLevel.RURAL_AUTONOME_PEU_DENSE,
      title: 'À environ 1h de route de mon établissement',
    },
    {
      level: InstitutionRuralLevel.URBAIN_DENSIT_INTERM_DIAIRE,
      title: 'À moins de 30 minutes de route de mon établissement',
    },
    { level: null, title: 'À moins de 30 minutes à pied de mon établissement' },
  ])(
    'should display the playlist title based on the institution rural level',
    async (ruralLevelParam) => {
      renderNewOfferPlaylist({
        ...user,
        institutionRuralLevel: ruralLevelParam.level,
      })

      expect(await screen.findByText(ruralLevelParam.title)).toBeInTheDocument()
    }
  )
})
