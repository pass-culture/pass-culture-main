import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { Events } from 'core/FirebaseEvents/constants'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface ActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  isDisabled: boolean
  nextStepTitle?: string
  nextTo?: SIGNUP_JOURNEY_STEP_IDS
  previousStepTitle?: string
  previousTo?: SIGNUP_JOURNEY_STEP_IDS
  hideRightButton?: boolean
  withRightIcon?: boolean
  legalCategoryCode?: string
}

export const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
  hideRightButton = false,
  nextStepTitle = 'Étape suivante',
  nextTo,
  previousStepTitle = 'Étape précédente',
  previousTo,
  withRightIcon = true,
  legalCategoryCode,
}: ActionBarProps) => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  const logActionBarNavigation = (to: SIGNUP_JOURNEY_STEP_IDS) => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to,
      used: OnboardingFormNavigationAction.ActionBar,
      categorieJuridiqueUniteLegale: legalCategoryCode,
    })
  }
  const Left = (): JSX.Element => {
    if (!onClickPrevious) {
      return <></>
    }

    return (
      <Button
        icon={fullLeftIcon}
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
      <Button
        type="submit"
        icon={withRightIcon ? fullRightIcon : undefined}
        iconPosition={IconPositionEnum.RIGHT}
        disabled={isDisabled}
        onClick={() => {
          onClickNext && onClickNext()
          nextTo && logActionBarNavigation(nextTo)
        }}
      >
        {nextStepTitle}
      </Button>
    )
  }

  return (
    <ActionsBarSticky hasSideNav={false}>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right>{Right()}</ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
