import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { Target } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { DEFAULT_ACTIVITY_VALUES } from 'commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { DEFAULT_OFFERER_FORM_VALUES } from 'components/SignupJourneyForm/Offerer/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'

import { SignupJourneyStepper } from '../SignupJourneyStepper'

const mockLogEvent = vi.fn()

const renderSignupJourneyStepper = (
  contextValue: SignupJourneyContextValues,
  url = '/parcours-inscription/authentification'
) => {
  const rtlReturns = renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <SignupJourneyStepper />
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

describe('test renderSignupJourneyStepper', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: () => {},
    }
  })
  it('should not log current tab click and disabled ones', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupJourneyStepper(contextValue)

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }

    expect(mockLogEvent).toHaveBeenCalledTimes(0)

    if (tabActivity) {
      await userEvent.click(tabActivity)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(0)

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(0)
  })

  it('should log breadcrumbs navigation to authentication', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication } = renderSignupJourneyStepper(
      contextValue,
      '/parcours-inscription/activite'
    )

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: OnboardingFormNavigationAction.Breadcrumb,
      }
    )
  })

  it('should not log breadcrumbs navigation to activity', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabActivity } = renderSignupJourneyStepper(
      contextValue,
      '/parcours-inscription/activite'
    )

    if (tabActivity) {
      await userEvent.click(tabActivity)
    }
    expect(mockLogEvent).not.toHaveBeenCalled()
  })

  it('should log breadcrumbs navigation', async () => {
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
      phoneNumber: undefined,
    }
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupJourneyStepper(
        contextValue,
        '/parcours-inscription/validation'
      )

    expect(screen.getByText('Validation screen')).toBeInTheDocument()

    if (tabActivity) {
      await userEvent.click(tabActivity)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/validation',
        to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
        used: OnboardingFormNavigationAction.Breadcrumb,
      }
    )

    if (tabValidation) {
      await userEvent.click(tabValidation)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
        used: OnboardingFormNavigationAction.Breadcrumb,
      }
    )

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(3)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      3,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/validation',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: OnboardingFormNavigationAction.Breadcrumb,
      }
    )
  })
})
