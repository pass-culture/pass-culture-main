import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { IActionBarProps } from 'screens/SignupJourneyForm/ActionBar/ActionBar'
import { ActionBar } from 'screens/SignupJourneyForm/ActionBar/index'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = jest.fn()

const renderActionBar = (props: IActionBarProps) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  const propsWithLogs = {
    ...props,
    ...{ logEvent: mockLogEvent },
  }

  return renderWithProviders(<ActionBar {...propsWithLogs} />, {
    storeOverrides,
    initialRouterEntries: ['/parcours-inscription/activite'],
  })
}

describe('screens:SignupJourney::ActionBar', () => {
  let props: IActionBarProps
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('Should log next action', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: false,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      logEvent: null,
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
      }
    )
  })

  it('Should log next action if disabled', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: true,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      logEvent: null,
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
      logEvent: null,
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
      }
    )
  })
})
