import React from 'react'
import { useLocation } from 'react-router-dom'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { logEventType } from 'context/analyticsContext'
import { Events } from 'core/FirebaseEvents/constants'
import { ReactComponent as IcoMiniArrowLeft } from 'icons/ico-mini-arrow-left.svg'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface IActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  isDisabled: boolean
  nextStepTitle?: string
  nextTo?: SIGNUP_JOURNEY_STEP_IDS
  previousStepTitle?: string
  previousTo?: SIGNUP_JOURNEY_STEP_IDS
  hideRightButton?: boolean
  withRightIcon?: boolean
  logEvent: logEventType | null
}

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
  hideRightButton = false,
  nextStepTitle = 'Étape suivante',
  nextTo,
  previousStepTitle = 'Étape précédente',
  previousTo,
  withRightIcon = true,
  logEvent,
}: IActionBarProps) => {
  const location = useLocation()

  const logActionBarNavigation = (to: SIGNUP_JOURNEY_STEP_IDS) => {
    logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to,
      used: OnboardingFormNavigationAction.ActionBar,
    })
  }
  const Left = (): JSX.Element => {
    if (!onClickPrevious) {
      return <></>
    }

    return (
      <Button
        Icon={IcoMiniArrowLeft}
        onClick={() => {
          onClickPrevious()
          previousTo && logActionBarNavigation(previousTo)
        }}
        variant={ButtonVariant.SECONDARY}
        disabled={isDisabled}
      >
        {previousStepTitle}
      </Button>
    )
  }

  const Right = (): JSX.Element | null => {
    if (hideRightButton) {
      return <></>
    }

    return (
      <SubmitButton
        Icon={withRightIcon ? IcoMiniArrowRight : undefined}
        iconPosition={IconPositionEnum.RIGHT}
        disabled={isDisabled}
        onClick={() => {
          onClickNext && onClickNext()
          nextTo && logActionBarNavigation(nextTo)
        }}
      >
        {nextStepTitle}
      </SubmitButton>
    )
  }

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right>{Right()}</ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default ActionBar
