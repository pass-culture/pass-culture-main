import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { Target } from 'apiClient/v1'
import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import {
  DEFAULT_ACTIVITY_VALUES,
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignupBreadcrumb from '../SignupJourneyBreadcrumb'

const mockLogEvent = jest.fn()

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
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    contextValue = {
      activity: DEFAULT_ACTIVITY_VALUES,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: () => {},
    }
  })
  it('Should not log current tab click and disabled ones', async () => {
    const { tabAuthentication, tabActivity, tabValidation } =
      renderSignupBreadcrumb(contextValue)

    tabAuthentication && (await userEvent.click(tabAuthentication))

    expect(mockLogEvent).toHaveBeenCalledTimes(0)

    tabActivity && (await userEvent.click(tabActivity))
    expect(mockLogEvent).toHaveBeenCalledTimes(0)

    tabValidation && (await userEvent.click(tabValidation))
    expect(mockLogEvent).toHaveBeenCalledTimes(0)
  })

  it('should log breadcrumbs navigation to authentication', async () => {
    contextValue.offerer = {
      name: 'test name',
      siret: '1234567893333',
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabAuthentication } = renderSignupBreadcrumb(
      contextValue,
      '/parcours-inscription/activite'
    )

    tabAuthentication && (await userEvent.click(tabAuthentication))
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
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    const { tabActivity } = renderSignupBreadcrumb(
      contextValue,
      '/parcours-inscription/activite'
    )

    tabActivity && (await userEvent.click(tabActivity))
    expect(mockLogEvent).not.toHaveBeenCalled()
  })

  it('should log breadcrumbs navigation', async () => {
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

    tabValidation && (await userEvent.click(tabValidation))
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

    tabAuthentication && (await userEvent.click(tabAuthentication))
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
