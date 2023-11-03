// @vitest-environment happy-dom
import { screen } from '@testing-library/react'
import React from 'react'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AdageDiscovery } from '../AdageDiscovery'

const renderAdageDiscovery = (user: AuthenticatedResponse) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <AdageDiscovery />
    </AdageUserContextProvider>
  )
}

describe('AdageDiscovery', () => {
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  it('should render adage discovery', () => {
    renderAdageDiscovery(user)

    expect(
      screen.getByText('Les nouvelles offres publiées')
    ).toBeInTheDocument()
  })
})
