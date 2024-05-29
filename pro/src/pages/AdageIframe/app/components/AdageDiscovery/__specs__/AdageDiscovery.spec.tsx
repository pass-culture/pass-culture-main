import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { api, apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import * as useIsElementVisible from 'hooks/useIsElementVisible'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AdageDiscovery } from '../AdageDiscovery'
import { DOMAINS_PLAYLIST } from '../constant'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: true,
  }),
})

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logHasSeenAllPlaylist: vi.fn(),
    logConsultPlaylistElement: vi.fn(),
    logHasSeenWholePlaylist: vi.fn(),
    newTemplateOffersPlaylist: vi.fn(),
  },
  api: {
    listEducationalDomains: vi.fn(() => [
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
    ]),
  },
}))

vi.mock('hooks/useIsElementVisible', () => ({
  useIsElementVisible: vi.fn(() => [false, false]),
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

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.default>
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
  })

  it('should render adage discovery', async () => {
    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(
      screen.getByText('Les offres publiées récemment')
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

  it('should call tracker when last playlist is visible', async () => {
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockImplementationOnce(
      () => [true]
    )

    renderAdageDiscovery(user)

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    expect(apiAdage.logHasSeenAllPlaylist).toHaveBeenCalledTimes(1)
  })

  it('should call tracker for domains playlist element', async () => {
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: '',
      },
      writable: true,
    })

    renderAdageDiscovery(user)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const link = await screen.findByRole('link', {
      name: 'Danse',
    })

    await userEvent.click(link)

    expect(apiAdage.logConsultPlaylistElement).toHaveBeenCalledWith(
      expect.objectContaining({
        elementId: 1,
        index: 0,
        playlistId: DOMAINS_PLAYLIST,
        playlistType: 'domain',
      })
    )
  })

  it('should trigger a log when the last element of a playlist is seen', async () => {
    renderAdageDiscovery(user)

    // log for each playlist
    vi.spyOn(useIsElementVisible, 'useIsElementVisible')
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])
      .mockReturnValueOnce([true, true])

    await waitFor(() => expect(api.listEducationalDomains).toHaveBeenCalled())

    //  Log called once for each playlist
    expect(apiAdage.logHasSeenWholePlaylist).toHaveBeenCalledTimes(4)
  })
})
