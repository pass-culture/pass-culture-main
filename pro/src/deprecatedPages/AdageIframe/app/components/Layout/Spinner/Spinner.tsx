import './Spinner.scss'
import React, { useEffect, useState } from 'react'

import { ReactComponent as LogoImage } from 'icons/ico-passculture.svg'

export const Spinner = ({
  message = 'Chargement en cours',
}: {
  message: string
}): JSX.Element => {
  const [numberOfDots, setNumberOfDots] = useState(3)

  useEffect(() => {
    let timer: string | number | NodeJS.Timeout | undefined
    if (message) {
      timer = setTimeout(
        () =>
          setNumberOfDots(currentNumberOfDots => (currentNumberOfDots % 3) + 1),
        500
      )
    }
    return () => clearTimeout(timer)
  }, [message, numberOfDots])

  return (
    <span className="loading-spinner" data-testid="spinner">
      <LogoImage className="ico-logo-passculture" />
      {message && (
        <span
          className="content"
          data-dots={Array(numberOfDots).fill('.').join('')}
        >
          {message}
        </span>
      )}
    </span>
  )
}
