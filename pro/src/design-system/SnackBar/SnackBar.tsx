import cx from 'classnames'
import fullClearIcon from 'icons/full-clear.svg'
import fullCloseIcon from 'icons/full-close.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { useCallback, useEffect, useRef, useState } from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SnackBar.module.scss'

const calculateDuration = (text: string): number => {
  return text.length <= 120 ? 5000 : 10000
}

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

  const duration = calculateDuration(text)

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

  const getIcon = (): string => {
    switch (variant) {
      case SnackBarVariant.ERROR:
        return fullClearIcon

      default:
        return fullValidateIcon
    }
  }

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
      role="alert"
      aria-live="polite"
      data-testid={testId}
    >
      <div className={cx(styles['wrapper'])}>
        <div className={cx(styles['content'])}>
          <div className={cx(styles['content-icon'])}>
            <SvgIcon
              src={getIcon()}
              alt={
                variant === SnackBarVariant.ERROR
                  ? "Icône d'erreur"
                  : 'Icône de succès'
              }
              width={'24'}
              className={styles['content-icon-svg']}
            />
          </div>
          <p className={cx(styles['content-text'])}>{text}</p>
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
