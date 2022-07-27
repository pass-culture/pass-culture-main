import cn from 'classnames'
import React, { useEffect, useState } from 'react'

import Icon from './Icon'

interface SpinnerProps {
  message?: string
  className?: string
}

const Spinner = ({
  message = 'Chargement en cours',
  className,
}: SpinnerProps): JSX.Element => {
  const [nbDots, setNbDots] = useState(3)
  const [timer, setTimer] = useState<number | null>(null)

  useEffect(() => {
    if (timer) window.clearInterval(timer)
    const newTimer = window.setInterval(() => {
      setNbDots(oldVal => (oldVal % 3) + 1)
    }, 500)
    setTimer(newTimer)
    return () => {
      window.clearInterval(newTimer)
    }
  }, [])

  return (
    <div className={cn('loading-spinner', className)} data-testid="spinner">
      <Icon svg="loader-pc" />
      <div className="content" data-dots={Array(nbDots).fill('.').join('')}>
        {message}
      </div>
    </div>
  )
}

export default Spinner
