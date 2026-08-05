import cn from 'classnames'
import { useLayoutEffect, useRef, useState } from 'react'
import { Link } from 'react-router'

import { noop } from '@/commons/utils/noop'

import styles from './Stepper.module.scss'

export const STEPPER_MIN_WIDTH_PER_STEP = 80

export interface StepItem {
  id: string
  label: string | React.ReactNode
  sublabel?: string
  url?: string
  onClick?: () => void
}

export interface StepperProps {
  steps: StepItem[]
  activeStep: string
  /**
   * Layout direction of the stepper.
   * - 'auto': horizontal on desktop (if space permits, >= 80px per step), vertical on mobile.
   * - 'horizontal': forced horizontal layout.
   * - 'vertical': forced vertical layout.
   */
  orientation?: 'horizontal' | 'vertical' | 'auto'
  ref?: React.RefObject<HTMLOListElement>
}

export const Stepper = ({
  steps,
  activeStep,
  orientation = 'auto',
  ref,
}: StepperProps): JSX.Element => {
  const fallbackRef = useRef<HTMLOListElement>(null)
  const listRef = (ref ||
    fallbackRef) as React.RefObject<HTMLOListElement | null>
  const [isVertical, setIsVertical] = useState(orientation === 'vertical')

  const activeStepIndex = steps.findIndex((step) => step.id === activeStep)

  // Bascule horizontal -> vertical based on width per step
  useLayoutEffect(() => {
    if (orientation !== 'auto') {
      setIsVertical(orientation === 'vertical')
      return noop
    }

    const listElement = listRef.current
    if (!listElement) {
      return noop
    }

    const checkResponsive = (width: number) => {
      const minWidthNeeded = steps.length * STEPPER_MIN_WIDTH_PER_STEP
      setIsVertical(width < minWidthNeeded)
    }

    // Check initially
    const initialRect = listElement.getBoundingClientRect()
    if (initialRect.width > 0) {
      checkResponsive(initialRect.width)
    }

    if (typeof window !== 'undefined' && 'ResizeObserver' in window) {
      const resizeObserver = new window.ResizeObserver((entries) => {
        for (const entry of entries) {
          const width = entry.contentRect.width
          if (width > 0) {
            checkResponsive(width)
          }
        }
      })

      resizeObserver.observe(listElement)
      return () => {
        resizeObserver.disconnect()
      }
    }

    return noop
  }, [steps.length, orientation, listRef])

  return (
    <ol
      ref={listRef}
      className={cn(
        styles.stepper,
        isVertical ? styles.vertical : styles.horizontal
      )}
    >
      {steps.map((step, index) => {
        // Steps are disabled by default if they are not yet reached
        let state: 'disabled' | 'current' | 'done' = 'disabled'
        if (index < activeStepIndex) {
          state = 'done'
        } else if (index === activeStepIndex) {
          state = 'current'
        }

        // Only completed steps are actionable:
        // the current step already shows its own content, and upcoming ones
        // are not reachable yet.
        const isActionable = state === 'done'
        const linkUrl = isActionable ? step.url : undefined
        const hasButton = isActionable && !step.url && !!step.onClick
        const isClickable = !!linkUrl || hasButton

        // Accessibility VoiceOver format
        const stateTranslation = {
          done: 'terminée',
          current: 'active',
          disabled: 'à venir',
        }[state]

        const voiceOverText = `Étape ${index + 1} sur ${steps.length}, ${stateTranslation}, ${step.label}`

        const visualContent = (
          <div className={styles['step-content']} aria-hidden="true">
            <div className={styles.indicator}>
              <span className={styles.number}>
                {(index + 1).toString().padStart(2, '0')}
              </span>
              {
                <div
                  className={cn(styles.connector, {
                    [styles.active]: state === 'done',
                  })}
                />
              }
            </div>
            <div className={styles['text-container']}>
              <span className={styles.label}>{step.label}</span>
              {step.sublabel && (
                <span className={styles.sublabel}>{step.sublabel}</span>
              )}
            </div>
          </div>
        )

        return (
          <li
            key={step.id}
            aria-current={state === 'current' ? 'step' : undefined}
            className={cn(styles['step-item'], styles[state], {
              [styles.clickable]: isClickable,
            })}
          >
            <StepTrigger
              linkUrl={linkUrl}
              hasButton={hasButton}
              onClick={step.onClick}
              voiceOverText={voiceOverText}
            >
              {visualContent}
            </StepTrigger>
          </li>
        )
      })}
    </ol>
  )
}

Stepper.displayName = 'Stepper'

function StepTrigger({
  linkUrl,
  hasButton,
  onClick,
  voiceOverText,
  children,
}: {
  linkUrl?: string
  hasButton: boolean
  onClick?: () => void
  voiceOverText: string
  children: React.ReactNode
}): JSX.Element {
  if (linkUrl) {
    return (
      <Link
        to={linkUrl}
        onClick={onClick}
        className={styles.link}
        aria-label={voiceOverText}
      >
        {children}
      </Link>
    )
  }

  if (hasButton) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={styles.button}
        aria-label={voiceOverText}
      >
        {children}
      </button>
    )
  }

  return (
    <div className={styles.wrapper}>
      <span className={styles['visually-hidden']}>{voiceOverText}</span>
      {children}
    </div>
  )
}
