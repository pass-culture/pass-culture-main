import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { Target } from 'apiClient/v1'
import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address'
import {
  DEFAULT_ACTIVITY_VALUES,
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignupBreadcrumb from '../SignupJourneyBreadcrumb'

const renderSignupBreadcrumb = (
  contextValue: ISignupJourneyContext,
  url = '/parcours-inscription/authentification'
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }
  const rtlReturns = renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <SignupBreadcrumb />
      <Routes>
        <Route
          path="/parcours-inscription/authentification"
          element={<div>Authentication screen</div>}
        />
        <Route
          path="/parcours-inscription/activite"
          element={<div>Activity screen</div>}
        />
        <Route
          path="/parcours-inscription/validation"
          element={<div>Validation screen</div>}
        />
      </Routes>
    </SignupJourneyContext.Provider>,
    { storeOverrides, initialRouterEntries: [url] }
  )

  const tabAuthentication = screen.queryByText('Identification')
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
  let contextValue: ISignupJourneyContext
  beforeEach(() => {
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: () => {},
    }
  })
  it('should render authentication step', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupBreadcrumb(contextValue)

    expect(tabAuthentication).toBeInTheDocument()
    expect(tabActivity).toBeInTheDocument()
    expect(tabValidation).toBeInTheDocument()

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()

    tabActivity && (await userEvent.click(tabActivity))
    expect(screen.queryByText('Activity screen')).not.toBeInTheDocument()

    tabValidation && (await userEvent.click(tabValidation))
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })

  it('should render activity step', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication, tabValidation } = renderSignupBreadcrumb(
      contextValue,
      '/parcours-inscription/activite'
    )

    expect(screen.getByText('Activity screen')).toBeInTheDocument()

    tabValidation && (await userEvent.click(tabValidation))
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()

    tabAuthentication && (await userEvent.click(tabAuthentication))
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should render validation step and navigate through steps', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    contextValue.activity = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL,
    }
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupBreadcrumb(contextValue, '/parcours-inscription/validation')

    expect(screen.getByText('Validation screen')).toBeInTheDocument()

    tabActivity && (await userEvent.click(tabActivity))
    expect(screen.getByText('Activity screen')).toBeInTheDocument()

    tabValidation && (await userEvent.click(tabValidation))
    expect(screen.getByText('Validation screen')).toBeInTheDocument()

    tabAuthentication && (await userEvent.click(tabAuthentication))
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()

    tabValidation && (await userEvent.click(tabValidation))
    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should not render breadcrumb when step is not included in breadcrumb step', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupBreadcrumb(contextValue, '/parcours-inscription/structure')

    expect(tabAuthentication).not.toBeInTheDocument()
    expect(tabActivity).not.toBeInTheDocument()
    expect(tabValidation).not.toBeInTheDocument()
  })
})
