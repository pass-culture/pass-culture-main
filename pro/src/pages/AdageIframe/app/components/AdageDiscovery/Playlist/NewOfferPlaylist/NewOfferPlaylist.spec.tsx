import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles, type AuthenticatedResponse } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import * as useIsElementVisible from '@/commons/hooks/useIsElementVisible'
import * as useNotification from '@/commons/hooks/useNotification'
import { defaultCollectiveTemplateOffer } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { NewOfferPlaylist } from './NewOfferPlaylist'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logConsultPlaylistElement: vi.fn(),
    newTemplateOffersPlaylist: vi.fn(),
  },
}))

const mockTrackPlaylistElementClicked = vi.fn()
const mockOnWholePlaylistSeen = vi.fn()

const renderNewOfferPlaylist = (user: AuthenticatedResponse) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <NewOfferPlaylist
        onWholePlaylistSeen={mockOnWholePlaylistSeen}
        trackPlaylistElementClicked={mockTrackPlaylistElementClicked}
      />
    </AdageUserContextProvider>
  )
}

describe('AdageDiscovery', () => {
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
    vi.spyOn(apiAdage, 'newTemplateOffersPlaylist').mockResolvedValue({
      collectiveOffers: [defaultCollectiveTemplateOffer],
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
    renderNewOfferPlaylist(user)

    expect(
      await screen.findByText('Les offres publiées récemment')
    ).toBeInTheDocument()
  })

  it('should call tracker for new offer playlist element', async () => {
    renderNewOfferPlaylist(user)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const newOfferPlaylistElement = await screen.findByText('Mon offre vitrine')
    newOfferPlaylistElement.addEventListener('click', (e) => {
      e.preventDefault()
    })
    await userEvent.click(newOfferPlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenNthCalledWith(1, {
      index: 0,
      offerId: 1,
      playlistId: 0,
      playlistType: 'offer',
    })
  })

  it('should call tracker when whole classroom playlist is seen', async () => {
    renderNewOfferPlaylist(user)
    vi.spyOn(useIsElementVisible, 'useIsElementVisible')
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(mockOnWholePlaylistSeen).toHaveBeenNthCalledWith(1, {
      playlistId: 0,
      playlistType: 'offer',
      numberOfTiles: 1,
    })
  })
})
