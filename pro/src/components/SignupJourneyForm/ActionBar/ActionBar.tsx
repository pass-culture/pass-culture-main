import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import type { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullLeftIcon from '@/icons/full-left.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'

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
}: ActionBarProps) => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  const logActionBarNavigation = (to: SIGNUP_JOURNEY_STEP_IDS) => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: location.pathname,
      to,
      used: SignupJourneyAction.ActionBar,
    })
  }
  const Left = () => {
    if (!onClickPrevious) {
      return null
    }

    return (
      <Button
        icon={fullLeftIcon}
        onClick={() => {
          onClickPrevious()
          if (previousTo) {
            logActionBarNavigation(previousTo)
          }
        }}
        type="button"
        variant={ButtonVariant.SECONDARY}
        disabled={isDisabled}
        label={previousStepTitle}
      />
    )
  }

  const Right = () => {
    if (hideRightButton) {
      return null
    }

    return (
      <Button
        type="submit"
        icon={withRightIcon ? fullRightIcon : undefined}
        iconPosition={IconPositionEnum.RIGHT}
        disabled={isDisabled}
        onClick={() => {
          onClickNext?.()
          if (nextTo) {
            logActionBarNavigation(nextTo)
          }
        }}
        label={nextStepTitle}
      />
    )
  }

  return (
    <ActionsBarSticky hasSideNav={false}>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right>{Right()}</ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
