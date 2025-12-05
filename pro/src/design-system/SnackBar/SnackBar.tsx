import cx from 'classnames'
import fullClearIcon from 'icons/full-clear.svg'
import fullCloseIcon from 'icons/full-close.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SnackBar.module.scss'

const SHORT_TEXT_DURATION = 5000
const LONG_TEXT_DURATION = 10000
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
   * The text of the snack bar
   */
  text: string
  /**
   * Whether the snack bar is visible or not
   */
  isVisible?: boolean
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
}

const ANIMATION_DURATION = 300 // Durée de l'animation en ms

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
  text,
  onClose,
  autoClose = true,
  isVisible = true,
  testId,
}: SnackBarProps): JSX.Element => {
  const [progress, setProgress] = useState(0)
  const [isClosing, setIsClosing] = useState(false)
  const hasClosedRef = useRef(false)
  const onCloseRef = useRef(onClose)

  const duration =
    text.length <= SHORT_TEXT_THRESHOLD
      ? SHORT_TEXT_DURATION
      : LONG_TEXT_DURATION

  // Garde toujours la dernière version de onClose
  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  // Reset state when visibility changes to true (new notification)
  useEffect(() => {
    if (isVisible) {
      setProgress(0)
      setIsClosing(false)
      hasClosedRef.current = false
    }
  }, [isVisible])

  // Safe close handler with exit animation (stable reference)
  const handleClose = useCallback(() => {
    if (hasClosedRef.current) {
      return
    }
    hasClosedRef.current = true
    setIsClosing(true)

    // Attendre la fin de l'animation avant d'appeler onClose
    setTimeout(() => {
      onCloseRef.current?.()
    }, ANIMATION_DURATION)
  }, []) // Pas de dépendances = référence stable

  const variantConfig = useMemo(() => VARIANT_CONFIG[variant], [variant])

  // Animation de la barre de progression
  useEffect(() => {
    if (!isVisible || isClosing) {
      return
    }

    const interval = setInterval(() => {
      setProgress((prev) => {
        const increment = (100 / duration) * 50
        return Math.min(prev + increment, 100)
      })
    }, 50)

    return () => clearInterval(interval)
  }, [duration, isVisible, isClosing])

  // Timer pour fermer automatiquement
  useEffect(() => {
    if (!autoClose || !isVisible) {
      return
    }

    const timer = setTimeout(() => {
      handleClose()
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, autoClose, isVisible, handleClose])

  return (
    <div
      className={cx(
        styles['container'],
        styles[variant],
        isClosing ? styles['hide'] : isVisible && styles['show']
      )}
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
            {text}
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
        <div
          className={cx(styles['progress-bar'])}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  )
}

SnackBar.displayName = 'SnackBar'
