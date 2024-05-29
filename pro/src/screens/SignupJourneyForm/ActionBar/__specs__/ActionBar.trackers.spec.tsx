import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { Events } from 'core/FirebaseEvents/constants'
import {
  ActionBarProps,
  ActionBar,
} from 'screens/SignupJourneyForm/ActionBar/ActionBar'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

const mockLogEvent = vi.fn()

const renderActionBar = (props: ActionBarProps) => {
  const propsWithLogs = {
    ...props,
    ...{ logEvent: mockLogEvent },
  }

  return renderWithProviders(<ActionBar {...propsWithLogs} />, {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: ['/parcours-inscription/activite'],
  })
}

describe('screens:SignupJourney::ActionBar', () => {
  let props: ActionBarProps
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should log next action', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: false,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
    }
    renderActionBar(props)

    await userEvent.click(screen.getByText('NEXT'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
        used: OnboardingFormNavigationAction.ActionBar,
        categorieJuridiqueUniteLegale: undefined,
      }
    )
  })

  it('should log next action if disabled', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: true,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
    }
    renderActionBar(props)

    await userEvent.click(screen.getByText('NEXT'))

    expect(mockLogEvent).toHaveBeenCalledTimes(0)
  })

  it('should log previous action', async () => {
    props = {
      onClickNext: () => null,
      onClickPrevious: () => null,
      nextStepTitle: 'NEXT',
      previousStepTitle: 'PREVIOUS',
      isDisabled: false,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      previousTo: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      legalCategoryCode: '1000',
    }
    renderActionBar(props)

    await userEvent.click(screen.getByText('PREVIOUS'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/parcours-inscription/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: OnboardingFormNavigationAction.ActionBar,
        categorieJuridiqueUniteLegale: '1000',
      }
    )
  })
})
