import React from 'react'

import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ActionBar.module.scss'

interface IActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  disablePrevious?: boolean
  disableNext?: boolean
}

const ActionBar = ({
  onClickPrevious,
  onClickNext,
  disablePrevious = false,
  disableNext = false,
}: IActionBarProps) => (
  <div className={style['action-bar']}>
    <div className={style['actions-group']}>
      {onClickPrevious && (
        <Button
          className={style['action']}
          disabled={disablePrevious}
          onClick={onClickPrevious}
        >
          Précédent
        </Button>
      )}
      <ButtonLink
        className={style['action']}
        link={{ to: '/offres', isExternal: false }}
        variant={ButtonVariant.SECONDARY}
      >
        Annuler
      </ButtonLink>
    </div>
    {onClickNext && (
      <Button
        className={style['action']}
        disabled={disableNext}
        onClick={onClickNext}
        style={{ justifySelf: 'flex-end' }}
      >
        Suivant
      </Button>
    )}
  </div>
)

export default ActionBar
