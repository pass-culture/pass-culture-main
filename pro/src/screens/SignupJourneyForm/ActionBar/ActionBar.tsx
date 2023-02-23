import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { SIGNUP_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { ReactComponent as IcoMiniArrowLeft } from 'icons/ico-mini-arrow-left.svg'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface IActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  isDisabled: boolean
  step: SIGNUP_STEP_IDS
  shouldTrack?: boolean
}

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
}: IActionBarProps) => {
  const Left = (): JSX.Element => {
    return (
      <Button
        Icon={IcoMiniArrowLeft}
        onClick={onClickPrevious}
        variant={ButtonVariant.SECONDARY}
        disabled={isDisabled}
      >
        Étape précédente
      </Button>
    )
  }

  const Right = (): JSX.Element | null => {
    return (
      <SubmitButton
        Icon={IcoMiniArrowRight}
        iconPosition={IconPositionEnum.RIGHT}
        disabled={isDisabled}
        onClick={onClickNext}
      >
        Étape suivante
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
