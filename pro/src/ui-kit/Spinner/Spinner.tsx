import cn from 'classnames'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import strokePass from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Spinner.module.scss'

interface SpinnerProps {
  message?: string
  className?: string
}

export const Spinner = ({ message, className }: SpinnerProps): JSX.Element => {
  const { t } = useTranslation('common')
  const [nbDots, setNbDots] = useState(3)
  const [timer, setTimer] = useState<number | null>(null)

  useEffect(() => {
    if (timer) {
      window.clearInterval(timer)
    }
    const newTimer = window.setInterval(() => {
      setNbDots((oldVal) => (oldVal % 3) + 1)
    }, 500)
    setTimer(newTimer)
    return () => {
      window.clearInterval(newTimer)
    }
  }, [])

  return (
    <div
      className={cn(styles['loading-spinner'], className)}
      data-testid="spinner"
    >
      <SvgIcon
        src={strokePass}
        alt=""
        className={styles['loading-spinner-icon']}
      />

      <div
        className={styles['content']}
        data-dots={Array(nbDots).fill('.').join('')}
      >
        {message || t('loading')}
      </div>
    </div>
  )
}
