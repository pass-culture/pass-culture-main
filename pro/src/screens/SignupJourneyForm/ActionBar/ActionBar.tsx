import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { ReactComponent as IcoMiniArrowLeft } from 'icons/ico-mini-arrow-left.svg'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface IActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  isDisabled: boolean
  nextStepTitle?: string
  previousStepTitle?: string
  hideRightButton?: boolean
  withRightIcon?: boolean
}

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
  hideRightButton = false,
  nextStepTitle = 'Étape suivante',
  previousStepTitle = 'Étape précédente',
  withRightIcon = true,
}: IActionBarProps) => {
  const Left = (): JSX.Element => {
    if (!onClickPrevious) {
      return <></>
    }

    return (
      <Button
        Icon={IcoMiniArrowLeft}
        onClick={onClickPrevious}
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
        onClick={onClickNext}
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
