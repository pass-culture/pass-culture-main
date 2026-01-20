import cx from 'classnames'
import fullClearIcon from 'icons/full-clear.svg'
import fullCloseIcon from 'icons/full-close.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { useCallback, useEffect, useRef, useState } from 'react'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SnackBar.module.scss'

export const SHORT_TEXT_DURATION = 5000
export const LONG_TEXT_DURATION = 10000
const SHORT_TEXT_THRESHOLD = 120

export enum SnackBarVariant {
  SUCCESS = 'success',
  ERROR = 'error',
}

export type SnackBarProps = {
  /**
   * The variant of the snack bar
   */
  variant?: SnackBarVariant
  /**
   * The description of the snack bar
   */
  description: string
  /**
   * The callback function to be called when the snack bar is closed
   */
  onClose?: () => void
  /**
   * The test id of the snack bar
   */
  testId?: string
  /**
   * Whether the snack bar should automatically close or not
   */
  autoClose?: boolean
  /**
   * Force the mobile view mode.
   */
  forceMobile?: boolean
}

export const ANIMATION_DURATION = 300 // should have the same value as `&.show transition` in `SnackBar.module.scss`

type VariantConfig = {
  icon: string
  ariaLabel: string
  role: 'alert' | 'status'
  ariaLive: 'assertive' | 'polite'
}

/**
 * Variant config is an object that contains the icon, aria label, role and aria live for each variant.
 * For adding a new variant, you need to add a new entry to the VARIANT_CONFIG object.
 * Maybe, we will need to add a new prop to the SnackBarProps to addd a new variant (Info, Warning, etc.)
 */
const VARIANT_CONFIG: Record<SnackBarVariant, VariantConfig> = {
  [SnackBarVariant.SUCCESS]: {
    icon: fullValidateIcon,
    ariaLabel: 'Message de succès',
    role: 'status',
    ariaLive: 'polite',
  },
  [SnackBarVariant.ERROR]: {
    icon: fullClearIcon,
    ariaLabel: "Message d'erreur",
    role: 'alert',
    ariaLive: 'assertive',
  },
}

export const SnackBar = ({
  variant = SnackBarVariant.SUCCESS,
  description,
  onClose,
  autoClose = true,
  testId,
  forceMobile = false,
}: SnackBarProps): JSX.Element => {
  const [isClosing, setIsClosing] = useState(false)
  const hasClosedRef = useRef(false)
  const onCloseRef = useRef(onClose)
  const isSmallScreen = useMediaQuery('(max-width: 38.125rem)')
  const isMobile = forceMobile || isSmallScreen

  // Keep onClose ref up to date without triggering re-renders
  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  const duration =
    description.length <= SHORT_TEXT_THRESHOLD
      ? SHORT_TEXT_DURATION
      : LONG_TEXT_DURATION

  // Safe close handler with exit animation
  const handleClose = useCallback(() => {
    if (hasClosedRef.current) {
      return
    }
    hasClosedRef.current = true
    setIsClosing(true)

    // Wait for the animation to finish before calling onClose
    setTimeout(() => {
      onCloseRef.current?.()
    }, ANIMATION_DURATION)
  }, [])

  const variantConfig = VARIANT_CONFIG[variant]

  // Automatically close timer
  useEffect(() => {
    if (!autoClose) {
      return
    }

    const timer = setTimeout(() => {
      handleClose()
    }, duration)

    return () => clearTimeout(timer)
  }, [autoClose, duration, handleClose])

  return (
    <div
      className={cx(
        styles['container'],
        styles[variant],
        isClosing ? styles['hide'] : styles['show'],
        isMobile ? styles['mobile'] : ''
      )}
      style={
        {
          '--snackbar-duration': `${duration}ms`,
          '--snackbar-animation-duration': `${ANIMATION_DURATION}ms`,
        } as React.CSSProperties
      }
      role={variantConfig.role}
      aria-live={variantConfig.ariaLive}
      aria-atomic="true"
      data-testid={testId}
    >
      <div className={cx(styles['wrapper'])}>
        <div className={cx(styles['content'])}>
          <div className={cx(styles['content-icon'])}>
            <SvgIcon
              src={variantConfig.icon}
              alt=""
              width={'24'}
              className={styles['content-icon-svg']}
            />
          </div>
          <p className={cx(styles['content-text'])}>
            <span className={styles['visually-hidden']}>
              {variantConfig.ariaLabel} :{' '}
            </span>
            {description}
          </p>
        </div>
        <div className={cx(styles['close-button-container'])}>
          <button
            className={cx(styles['close-button'])}
            type="button"
            onClick={handleClose}
            aria-label="Fermer le message"
          >
            <SvgIcon
              src={fullCloseIcon}
              alt={''}
              width={'24'}
              className={styles['close-button-svg']}
            />
          </button>
        </div>
      </div>
      {/* Dynamic progress bar */}
      <div className={cx(styles['progress-bar-container'])}>
        <div className={cx(styles['progress-bar'])}></div>
      </div>
    </div>
  )
}

SnackBar.displayName = 'SnackBar'
