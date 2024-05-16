import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { Target } from 'apiClient/v1'
import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { DEFAULT_ACTIVITY_VALUES } from 'context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SignupJourneyStepper } from '../SignupJourneyStepper'

const renderSignupStepper = (
  contextValue: SignupJourneyContextValues,
  url = '/parcours-inscription/identification'
) => {
  const rtlReturns = renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <SignupJourneyStepper />
      <Routes>
        <Route
          path={'/parcours-inscription/identification'}
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
    { user: sharedCurrentUserFactory(), initialRouterEntries: [url] }
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

describe('test SignupJourneyStepper', () => {
  let contextValue: SignupJourneyContextValues
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
      renderSignupStepper(contextValue)

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
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication, tabValidation } = renderSignupStepper(
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
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    contextValue.activity = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL,
    }
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupStepper(contextValue, '/parcours-inscription/validation')

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

  it('should not render stepper when step is not included in steps', () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupStepper(contextValue, '/parcours-inscription/structure')

    expect(tabAuthentication).not.toBeInTheDocument()
    expect(tabActivity).not.toBeInTheDocument()
    expect(tabValidation).not.toBeInTheDocument()
  })
})
