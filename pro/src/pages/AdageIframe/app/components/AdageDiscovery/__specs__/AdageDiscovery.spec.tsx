// @vitest-environment happy-dom
import { screen, waitFor } from '@testing-library/react'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AdageDiscovery } from '../AdageDiscovery'

vi.mock('apiClient/api', () => ({
  api: {
    listEducationalDomains: vi.fn(() => [
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
    ]),
  },
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

  it('should render adage discovery', () => {
    renderAdageDiscovery(user)

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
})
