import cn from 'classnames'
import React, { useEffect, useState } from 'react'

import strokePass from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

interface SpinnerProps {
  message?: string
  className?: string
  isLoading?: boolean
}

const Spinner = ({
  message = 'Chargement en cours',
  className,
  isLoading = true,
}: SpinnerProps): JSX.Element => {
  const [nbDots, setNbDots] = useState(3)
  const [timer, setTimer] = useState<number>()

  useEffect(() => {
    if (isLoading) {
      if (timer) {
        window.clearInterval(timer)
      }
      const newTimer = window.setInterval(() => {
        setNbDots((oldVal) => (oldVal % 3) + 1)
      }, 500)
      setTimer(newTimer)
    }
    return () => {
      window.clearInterval(timer)
    }
  }, [isLoading])

  return (
    <div className={cn('loading-spinner', className)} role="alert">
      {isLoading && (
        <>
          <SvgIcon src={strokePass} alt="" className="loading-spinner-icon" />

          <div
            data-testid="spinner"
            className="content"
            data-dots={Array(nbDots).fill('.').join('')}
          >
            {message}
          </div>
        </>
      )}
    </div>
  )
}

export default Spinner
