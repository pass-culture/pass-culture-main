import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { Target } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '@/components/SignupJourneyForm/Offerer/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

import { SignupJourneyStepper } from '../SignupJourneyStepper'

const mockLogEvent = vi.fn()

const renderSignupJourneyStepper = (
  contextValue: SignupJourneyContextValues,
  url = '/inscription/structure/authentification'
) => {
  const rtlReturns = renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <SignupJourneyStepper />
      <Routes>
        <Route
          path="/inscription/structure/authentification"
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
      initialAddress: null,
      setInitialAddress: noop,
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
      isDiffusible: true,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication } = renderSignupJourneyStepper(
      contextValue,
      '/inscription/structure/activite'
    )

    if (tabAuthentication) {
      await userEvent.click(tabAuthentication)
    }
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/inscription/structure/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: SignupJourneyAction.Breadcrumb,
      }
    )
  })

  it('should not log breadcrumbs navigation to activity', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      hasVenueWithSiret: false,
      isDiffusible: true,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabActivity } = renderSignupJourneyStepper(
      contextValue,
      '/inscription/structure/activite'
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
      renderSignupJourneyStepper(
        contextValue,
        '/inscription/structure/confirmation'
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
        from: '/inscription/structure/confirmation',
        to: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
        used: SignupJourneyAction.Breadcrumb,
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
        from: '/inscription/structure/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
        used: SignupJourneyAction.Breadcrumb,
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
        from: '/inscription/structure/confirmation',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: SignupJourneyAction.Breadcrumb,
      }
    )
  })
})
