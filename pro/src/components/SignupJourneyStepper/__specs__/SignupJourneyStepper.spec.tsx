import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { Target } from '@/apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'

import { SignupJourneyStepper } from '../SignupJourneyStepper'

const renderSignupStepper = (
  contextValue: SignupJourneyContextValues,
  url = '/inscription/structure/identification'
) => {
  const rtlReturns = renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <SignupJourneyStepper />
      <Routes>
        <Route
          path={'/inscription/structure/identification'}
          element={<div>Authentication screen</div>}
        />
        <Route
          path="/inscription/structure/activite"
          element={<div>Activity screen</div>}
        />
        <Route
          path="/inscription/structure/confirmation"
          element={<div>Validation screen</div>}
        />
      </Routes>
    </SignupJourneyContext.Provider>,
    { user: sharedCurrentUserFactory(), initialRouterEntries: [url] }
  )

  const tabAuthentication = screen.queryByText('Vos informations')
  const tabActivity = screen.queryByText('Votre activité')
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
      initialAddress: null,
      setInitialAddress: noop,
    }
  })
  it('should render authentication step', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupStepper(contextValue)

    expect(tabAuthentication).toBeInTheDocument()
    expect(tabActivity).toBeInTheDocument()
    expect(tabValidation).toBeInTheDocument()

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()

    if (tabActivity) {
      await userEvent.click(tabActivity)
    }

    await waitFor(() => {
      expect(screen.queryByText('Activity screen')).not.toBeInTheDocument()
    })

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })

  it('should render activity step', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      hasVenueWithSiret: false,
      isDiffusible: true,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication, tabValidation } = renderSignupStepper(
      contextValue,
      '/inscription/structure/activite'
    )

    expect(screen.getByText('Activity screen')).toBeInTheDocument()

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should render validation step and navigate through steps', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      hasVenueWithSiret: false,
      isDiffusible: true,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    contextValue.activity = {
      activity: 'MUSEUM',
      socialUrls: [],
      targetCustomer: Target.INDIVIDUAL,
      phoneNumber: '',
      culturalDomains: undefined,
    }
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupStepper(contextValue, '/inscription/structure/confirmation')

    expect(screen.getByText('Validation screen')).toBeInTheDocument()

    if (tabActivity) {
      await userEvent.click(tabActivity)
    }
    expect(screen.getByText('Activity screen')).toBeInTheDocument()

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(screen.getByText('Validation screen')).toBeInTheDocument()

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(screen.getByText('Validation screen')).toBeInTheDocument()
  })

  it('should not render stepper when step is not included in steps', () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupStepper(contextValue, '/inscription/structure/recherche')

    expect(tabAuthentication).not.toBeInTheDocument()
    expect(tabActivity).not.toBeInTheDocument()
    expect(tabValidation).not.toBeInTheDocument()
  })
})
