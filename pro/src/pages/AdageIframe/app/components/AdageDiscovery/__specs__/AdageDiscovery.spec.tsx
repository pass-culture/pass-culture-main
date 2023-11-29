// @vitest-environment happy-dom
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { api, apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useIsElementVisible from 'hooks/useIsElementVisible'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AdageDiscovery } from '../AdageDiscovery'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logHasSeenAllPlaylist: vi.fn(),
    logConsultPlaylistElement: vi.fn(),
    logHasSeenWholePlaylist: vi.fn(),
  },
  api: {
    listEducationalDomains: vi.fn(() => [
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
    ]),
  },
}))

vi.mock('hooks/useIsElementVisible', () => ({
  default: vi.fn().mockImplementation(() => [false, false]),
}))

const renderAdageDiscovery = (user: AuthenticatedResponse) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <AdageDiscovery />
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

  beforeEach(() => {
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useNotification'),
      error: notifyError,
    }))
  })

  it('should render adage discovery', async () => {
    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(
      screen.getByText('Les nouvelles offres publiées')
    ).toBeInTheDocument()
  })

  it('should render artistic domains playlist', async () => {
    renderAdageDiscovery(user)

    expect(
      await screen.findByRole('link', {
        name: 'Danse',
      })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('link', {
        name: 'Architecture',
      })
    ).toBeInTheDocument()
  })

  it('should show an error message notification when domains could not be fetched', async () => {
    vi.spyOn(api, 'listEducationalDomains').mockRejectedValueOnce(null)

    renderAdageDiscovery(user)
    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(notifyError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
  })

  it('should not call tracker when footer suggestion is not visible', async () => {
    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(apiAdage.logHasSeenAllPlaylist).toHaveBeenCalledTimes(0)
  })

  it('should call tracker when footer suggestion is visible', async () => {
    vi.spyOn(useIsElementVisible, 'default').mockReturnValueOnce([true])

    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(apiAdage.logHasSeenAllPlaylist).toHaveBeenCalledTimes(1)
  })

  it('should call tracker for new offer playlist element', async () => {
    renderAdageDiscovery(user)

    const newOfferPlaylistElement = screen.getByText('Ma super offre')

    await userEvent.click(newOfferPlaylistElement)

    expect(apiAdage.logConsultPlaylistElement).toHaveBeenCalledWith({
      elementId: 1,
      iframeFrom: '/',
      playlistId: 0,
      playlistType: 'offer',
    })
  })

  it('should call tracker for venue playlist element', async () => {
    renderAdageDiscovery(user)

    const venuePlaylistElement = screen.getByText(
      'Mon super lieu sur vraiment beaucoup de super lignes'
    )

    await userEvent.click(venuePlaylistElement)

    expect(apiAdage.logConsultPlaylistElement).toHaveBeenCalledWith({
      elementId: 1,
      iframeFrom: '/',
      playlistId: 3,
      playlistType: 'venue',
    })
  })

  it('should call tracker for domains playlist element', async () => {
    renderAdageDiscovery(user)

    const domainPlaylistElement = await screen.findByRole('link', {
      name: 'Danse',
    })

    await userEvent.click(domainPlaylistElement)

    expect(apiAdage.logConsultPlaylistElement).toHaveBeenCalledWith({
      elementId: 1,
      iframeFrom: '/',
      playlistId: 1,
      playlistType: 'domain',
    })
  })

  it('should trigger a log wheen the last element of a playlist is seen', async () => {
    //  Once for the footer visibility and twice for each playlist (4*2+1=9)
    vi.spyOn(useIsElementVisible, 'default')
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])

    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    //  Log called once for each playlist
    expect(apiAdage.logHasSeenWholePlaylist).toHaveBeenCalledTimes(4)
  })
})
