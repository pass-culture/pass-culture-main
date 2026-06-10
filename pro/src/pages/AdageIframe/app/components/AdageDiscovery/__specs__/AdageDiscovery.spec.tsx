import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  AdageFrontRoles,
  type AuthenticatedResponse,
} from '@/apiClient/adage/new'
import { apiAdageNew, apiNew } from '@/apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useIsElementVisible from '@/commons/hooks/useIsElementVisible'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { AdageDiscovery } from '../AdageDiscovery'
import { DOMAINS_PLAYLIST } from '../constant'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: true,
  }),
})

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    listEducationalDomains: vi.fn(),
  },
  apiAdageNew: {
    saveRedactorPreferences: vi.fn(),
    logHasSeenAllPlaylist: vi.fn(),
    logConsultPlaylistElement: vi.fn(),
    logHasSeenWholePlaylist: vi.fn(),
    newTemplateOffersPlaylist: vi.fn(),
  },
}))

vi.mock('@/commons/hooks/useIsElementVisible', () => ({
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
  const snackBarError = vi.fn()
  const adageUser = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  beforeEach(async () => {
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))

    vi.spyOn(apiNew, 'listEducationalDomains').mockResolvedValue([
      { id: 1, name: 'Danse', nationalPrograms: [] },
      { id: 2, name: 'Architecture', nationalPrograms: [] },
    ])
  })

  it('should render adage discovery', async () => {
    renderAdageDiscovery(adageUser)

    await waitFor(() =>
      expect(apiNew.listEducationalDomains).toHaveBeenCalled()
    )

    expect(
      screen.getByText('Les offres publiées récemment')
    ).toBeInTheDocument()
  })

  it('should render artistic domains playlist', async () => {
    renderAdageDiscovery(adageUser)

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

  it('should not call tracker when footer suggestion is not visible', async () => {
    renderAdageDiscovery(adageUser)

    await waitFor(() =>
      expect(apiNew.listEducationalDomains).toHaveBeenCalled()
    )

    expect(apiAdageNew.logHasSeenAllPlaylist).toHaveBeenCalledTimes(0)
  })

  it('should call tracker when last playlist is visible', async () => {
    vi.spyOn(useIsElementVisible, 'useIsElementVisible').mockImplementationOnce(
      () => [true]
    )

    renderAdageDiscovery(adageUser)

    await waitFor(() =>
      expect(apiNew.listEducationalDomains).toHaveBeenCalled()
    )

    expect(apiAdageNew.logHasSeenAllPlaylist).toHaveBeenCalledTimes(1)
  })

  it('should call tracker for domains playlist element', async () => {
    renderAdageDiscovery(adageUser)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const link = await screen.findByRole('link', {
      name: 'Danse',
    })

    await userEvent.click(link)

    expect(apiAdageNew.logConsultPlaylistElement).toHaveBeenCalledWith(
      expect.objectContaining({
        body: {
          domainId: 1,
          index: 0,
          playlistId: DOMAINS_PLAYLIST,
          playlistType: 'domain',
          iframeFrom: '/',
        },
      })
    )
  })

  it('should trigger a log when the last element of a playlist is seen', async () => {
    renderAdageDiscovery(adageUser)

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

    await waitFor(() =>
      expect(apiNew.listEducationalDomains).toHaveBeenCalled()
    )

    //  Log called once for each playlist
    expect(apiAdageNew.logHasSeenWholePlaylist).toHaveBeenCalledTimes(4)
  })

  it('should display error message when educational domains API fails', async () => {
    vi.spyOn(apiNew, 'listEducationalDomains').mockRejectedValueOnce(
      new Error('API Error')
    )

    renderAdageDiscovery(adageUser)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    })
  })

  describe('survey satisfaction', () => {
    it('should display survey satisfaction', async () => {
      renderAdageDiscovery(adageUser)

      const surveySatisfaction = await screen.findByText(
        'Enquête de satisfaction'
      )
      expect(surveySatisfaction).toBeVisible()
    })

    it('should not display survey satisfaction if user role readonly', async () => {
      renderAdageDiscovery({
        ...adageUser,
        role: AdageFrontRoles.READONLY,
      })

      await waitFor(() => {
        const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
        expect(surveySatisfaction).not.toBeInTheDocument()
      })
    })

    it('should not display survey satisfaction', async () => {
      renderAdageDiscovery({
        ...adageUser,
        preferences: { feedback_form_closed: true },
      })
      await waitFor(() => {
        const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
        expect(surveySatisfaction).not.toBeInTheDocument()
      })
    })

    it('should hide survey satisfaction when closed', async () => {
      const user = userEvent.setup()

      renderAdageDiscovery(adageUser)

      screen.getByText('Enquête de satisfaction')

      const closeButton = screen.getByRole('button', {
        name: 'J’ai déjà répondu',
      })

      await user.click(closeButton)

      expect(
        screen.queryByText('Enquête de satisfaction')
      ).not.toBeInTheDocument()
    })
  })
})
