import React from 'react'

import { ReactComponent as fullClear } from 'icons/full-clear.svg'
import { ReactComponent as fullSearch } from 'icons/full-search.svg'
import Button from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ModalFilterLayout.module.scss'

export interface ModalFilterLayoutProps
  extends React.HTMLProps<HTMLButtonElement> {
  title: string
}

const ModalFilterLayout = ({ title, children }: ModalFilterLayoutProps) => {
  return (
    <div className={styles['modal-content']}>
      <div className={styles['modal-content-title']}>{title}</div>
      <div className={styles['modal-content-children']}>{children}</div>
      <div className={styles['modal-content-separator']}></div>
      <div className={styles['modal-content-footer']}>
        <Button Icon={fullClear} variant={ButtonVariant.TERNARY}>
          Retour
        </Button>
        <Button
          Icon={fullSearch}
          variant={ButtonVariant.TERNARY}
          className={styles['search-button']}
        >
          Rechercher
        </Button>
      </div>
    </div>
  )
}

export default ModalFilterLayout
