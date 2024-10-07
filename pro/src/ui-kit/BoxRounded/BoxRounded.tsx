import cn from 'classnames'
import React from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './BoxRounded.module.scss'

interface BoxRoundedProps {
  children: React.ReactNode
  className?: string
  onClickModify?: () => void
  showButtonModify?: boolean
}

export const BoxRounded = ({
  children,
  className,
  onClickModify,
  showButtonModify = true,
}: BoxRoundedProps) => {
  const displayEditButton = showButtonModify && !!onClickModify

  return (
    <div
      className={cn(styles['expandable-box'], className, {
        [styles['expandable-box-closed']]: displayEditButton,
      })}
    >
      {displayEditButton && (
        <div className={styles['modify-button-container']}>
          <Button
            variant={ButtonVariant.TERNARY}
            onClick={onClickModify}
            icon={fullEditIcon}
          >
            Modifier
          </Button>
        </div>
      )}
      {children}
    </div>
  )
}
