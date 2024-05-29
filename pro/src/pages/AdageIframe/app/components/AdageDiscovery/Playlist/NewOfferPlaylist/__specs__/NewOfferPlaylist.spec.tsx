import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { NewOfferPlaylist } from '../NewOfferPlaylist'

vi.mock('apiClient/api', () => ({
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

  it('should render new offer playlist', async () => {
    renderNewOfferPlaylist(user)

    expect(
      await screen.findByText('Les offres publiées récemment')
    ).toBeInTheDocument()
  })

  it('should show an error message notification when offer could not be fetched', async () => {
    vi.spyOn(apiAdage, 'newTemplateOffersPlaylist').mockRejectedValueOnce(null)

    renderNewOfferPlaylist(user)
    await waitFor(() =>
      expect(apiAdage.newTemplateOffersPlaylist).toHaveBeenCalled()
    )

    expect(notifyError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
  })

  it('should call tracker for new offer playlist element', async () => {
    renderNewOfferPlaylist(user)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const newOfferPlaylistElement = await screen.findByText('Mon offre vitrine')
    newOfferPlaylistElement.addEventListener('click', (e) => {
      e.preventDefault()
    })
    await userEvent.click(newOfferPlaylistElement)

    expect(mockTrackPlaylistElementClicked).toHaveBeenCalledTimes(1)
  })
})
