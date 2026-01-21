import type React from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'

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
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              onClick={onClean}
              label="Réinitialiser"
            />
            <Button
              variant={ButtonVariant.PRIMARY}
              className={styles['search-button']}
              onClick={onSearch}
              data-testid="search-button-modal"
              type="submit"
              label="Rechercher"
            />
          </div>
        </>
      )}
    </div>
  )
}
