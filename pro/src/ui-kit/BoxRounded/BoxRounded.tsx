import cn from 'classnames'
import React from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './BoxRounded.module.scss'

interface BoxRoundedProps {
  children: JSX.Element
  onClickModify: () => void
  showButtonModify?: boolean
}

export const BoxRounded = ({
  children,
  onClickModify,
  showButtonModify = true,
}: BoxRoundedProps) => {
  return (
    <div
      className={cn(styles['expandable-box'], {
        [styles['expandable-box-closed']]: showButtonModify,
      })}
    >
      <div
        className={cn(styles['modify-button-container'], {
          [styles['hidden']]: !showButtonModify,
        })}
      >
        <Button
          variant={ButtonVariant.TERNARY}
          onClick={() => onClickModify()}
          icon={fullEditIcon}
        >
          Modifier
        </Button>
      </div>

      {children}
    </div>
  )
}
