import cn from 'classnames'
import React from 'react'

import { ReactComponent as EditIcon } from 'icons/ico-pen-black.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './BoxRounded.module.scss'

export interface IBoxRoundedProps {
  children: JSX.Element
  onClickModify: () => void
  showButtonModify?: boolean
}

const BoxRounded = ({
  children,
  onClickModify,
  showButtonModify = true,
}: IBoxRoundedProps) => {
  return (
    <div className={styles['expandable-box']}>
      <div
        className={cn(styles['modify-button-container'], {
          [styles['hidden']]: !showButtonModify,
        })}
      >
        <Button
          variant={ButtonVariant.TERNARY}
          onClick={() => onClickModify()}
          Icon={() => <EditIcon />}
        >
          Modifier
        </Button>
      </div>

      {children}
    </div>
  )
}

export default BoxRounded
