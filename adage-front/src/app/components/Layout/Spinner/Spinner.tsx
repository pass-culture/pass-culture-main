import './Spinner.scss'
import React, { useEffect, useState } from 'react'

import { ReactComponent as LogoImage } from 'assets/logo-without-text.svg'

export const Spinner = ({
  message = 'Chargement en cours',
}: {
  message: string
}): JSX.Element => {
  const [numberOfDots, setNumberOfDots] = useState(3)

  useEffect(() => {
    let timer
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
      <LogoImage />
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
