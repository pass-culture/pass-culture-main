import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { renderWithProviders } from 'utils/renderWithProviders'

import SignupBreadcrumb from '../SignupJourneyBreadcrumb'

const renderSignupBreadcrumb = (
  url = '/parcours-inscription/authentification',
  storeOverrides = {}
) => {
  const rtlReturns = renderWithProviders(
    <>
      <SignupBreadcrumb />
      <Routes>
        <Route
          path={'/parcours-inscription/authentification'}
          element={<div>Authentication screen</div>}
        />
        <Route
          path={'/parcours-inscription/activite'}
          element={<div>Activity screen</div>}
        />
        <Route
          path={'/parcours-inscription/validation'}
          element={<div>Validation screen</div>}
        />
      </Routes>
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )

  const tabAuthentication = screen.queryByText('Authentification')
  const tabActivity = screen.queryByText('Activité')
  const tabValidation = screen.queryByText('Validation')

  return {
    ...rtlReturns,
    tabAuthentication,
    tabActivity,
    tabValidation,
  }
}

describe('test SignupBreadcrumb', () => {
  it('should render steps', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupBreadcrumb()

    expect(tabAuthentication).toBeInTheDocument()
    expect(tabActivity).toBeInTheDocument()
    expect(tabValidation).toBeInTheDocument()

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()

    tabActivity && (await userEvent.click(tabActivity))
    expect(screen.getByText('Activity screen')).toBeInTheDocument()

    tabValidation && (await userEvent.click(tabValidation))
    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })
})
