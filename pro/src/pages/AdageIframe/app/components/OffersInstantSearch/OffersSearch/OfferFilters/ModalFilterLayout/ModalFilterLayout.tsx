import React from 'react'

import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ModalFilterLayout.module.scss'

interface ModalFilterLayoutProps extends React.HTMLProps<HTMLButtonElement> {
  title?: string
  hideFooter?: boolean
  onClean?: () => void
  onSearch?: () => void
}

export const ModalFilterLayout = ({
  title,
  hideFooter = false,
  children,
  onClean,
  onSearch,
}: ModalFilterLayoutProps) => {
  return (
    <div className={styles['modal-content']}>
      {title && <div className={styles['modal-content-title']}>{title}</div>}
      <div className={styles['modal-content-children']}>{children}</div>
      {!hideFooter && (
        <>
          <div className={styles['modal-content-separator']} />
          <div className={styles['modal-content-footer']}>
            <Button
              icon={fullRefreshIcon}
              variant={ButtonVariant.TERNARY}
              onClick={onClean}
            >
              Réinitialiser
            </Button>
            <Button
              variant={ButtonVariant.PRIMARY}
              className={styles['search-button']}
              onClick={onSearch}
              testId="search-button-modal"
            >
              Rechercher
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
