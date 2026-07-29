import cx from 'classnames'
import { type ReactNode, useId, useRef } from 'react'

import { Button } from '@/design-system/Button/Button'
import { Spinner } from '@/design-system/Button/components/Spinner/Spinner'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullCloseIcon from '@/icons/full-close.svg'
import fullLeftIcon from '@/icons/full-left.svg'
import { BaseDialog } from '@/ui-kit/BaseDialog/BaseDialog'

import styles from './DetailedModal.module.scss'

type DetailedModalLoadingState = {
  label: ReactNode
}

export type DetailedModalProps = {
  isOpen: boolean
  onClose: () => void
  title: ReactNode
  description?: ReactNode
  onGoBack?: () => void
  goBackButtonAriaLabel?: string
  primaryAction?: ReactNode
  secondaryAction?: ReactNode
  tertiaryAction?: ReactNode
  footerMessage?: ReactNode
  isFooterFixed?: boolean
  loadingState?: DetailedModalLoadingState
  ariaDescribedBy?: string
  children: ReactNode
}

export const DetailedModal = ({
  isOpen,
  onClose,
  title,
  description,
  onGoBack,
  goBackButtonAriaLabel = 'Retourner à l’étape précédente',
  primaryAction,
  secondaryAction,
  tertiaryAction,
  footerMessage,
  isFooterFixed = false,
  loadingState,
  ariaDescribedBy,
  children,
}: DetailedModalProps): JSX.Element => {
  const titleId = useId()
  const descriptionId = useId()
  const loadingDescriptionId = useId()
  const closeButtonRef = useRef<HTMLButtonElement | HTMLAnchorElement>(null)
  const isLoadingState = Boolean(loadingState)
  const hasActions = Boolean(primaryAction || secondaryAction || tertiaryAction)

  let computedDescriptionId: string | undefined
  if (isLoadingState) {
    computedDescriptionId = loadingDescriptionId
  } else if (description) {
    computedDescriptionId = descriptionId
  }
  const dialogAriaDescribedBy = ariaDescribedBy ?? computedDescriptionId

  const footerElement = !isLoadingState && hasActions && (
    <footer className={styles['detailed-modal-footer']}>
      <div className={styles['detailed-modal-main-actions']}>
        {tertiaryAction}
        {secondaryAction}
        <div className={styles['detailed-modal-primary-group']}>
          {primaryAction}
          {footerMessage && (
            <p className={styles['detailed-modal-footer-message']}>
              {footerMessage}
            </p>
          )}
        </div>
      </div>
    </footer>
  )

  return (
    <BaseDialog
      isOpen={isOpen}
      onClose={onClose}
      ariaLabelledBy={titleId}
      ariaDescribedBy={dialogAriaDescribedBy}
    >
      <div
        className={cx(styles['detailed-modal'], {
          [styles['detailed-modal-fixed-footer']]: isFooterFixed,
        })}
      >
        <header className={styles['detailed-modal-header']}>
          <div className={styles['detailed-modal-close-button']}>
            <Button
              ref={closeButtonRef}
              autoFocus
              icon={fullCloseIcon}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              onClick={onClose}
              aria-label={'Fermer la boite de dialogue'}
            />
          </div>
          <div className={styles['detailed-modal-header-left']}>
            {onGoBack && (
              <div className={styles['detailed-modal-go-back-button']}>
                <Button
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullLeftIcon}
                  aria-label={goBackButtonAriaLabel}
                  onClick={onGoBack}
                />
              </div>
            )}
            <h2 id={titleId} className={styles['detailed-modal-title']}>
              {title}
            </h2>
          </div>
        </header>

        {isLoadingState ? (
          <div
            id={loadingDescriptionId}
            className={styles['detailed-modal-loading']}
          >
            <Spinner />
            <p className={styles['detailed-modal-loading-label']}>
              {loadingState?.label}
            </p>
          </div>
        ) : (
          <div className={styles['detailed-modal-body']}>
            {description && (
              <p
                id={descriptionId}
                className={styles['detailed-modal-description']}
              >
                {description}
              </p>
            )}

            <div className={styles['detailed-modal-content']}>{children}</div>
          </div>
        )}

        {footerElement}
      </div>
    </BaseDialog>
  )
}
