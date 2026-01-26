import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import {
  ActionBar,
  type ActionBarProps,
} from '@/components/SignupJourneyForm/ActionBar/ActionBar'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

const mockLogEvent = vi.fn()

const renderActionBar = (props: ActionBarProps) => {
  const propsWithLogs = {
    ...props,
    ...{ logEvent: mockLogEvent },
  }

  return renderWithProviders(<ActionBar {...propsWithLogs} />, {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: ['/inscription/structure/activite'],
  })
}

describe('screens:SignupJourney::ActionBar', () => {
  let props: ActionBarProps
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should log next action', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: false,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
    }
    renderActionBar(props)

    await userEvent.click(screen.getByText('NEXT'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/inscription/structure/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
        used: SignupJourneyAction.ActionBar,
      }
    )
  })

  it('should log next action if disabled', async () => {
    props = {
      onClickNext: () => null,
      nextStepTitle: 'NEXT',
      isDisabled: true,
      nextTo: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
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
      nextTo: SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION,
      previousTo: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
    }
    renderActionBar(props)

    await userEvent.click(screen.getByText('PREVIOUS'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/inscription/structure/activite',
        to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
        used: SignupJourneyAction.ActionBar,
      }
    )
  })
})
