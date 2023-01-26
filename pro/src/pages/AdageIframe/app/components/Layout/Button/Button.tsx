import './Button.scss'
import React, { useCallback, useState } from 'react'

import { Spinner } from '../Spinner/Spinner'

export const Button = ({
  disabled,
  onClick,
  loadingMessage,
  text,
  isSubmit,
}: {
  disabled: boolean
  onClick: () => Promise<any>
  loadingMessage: string
  text: string
  isSubmit: boolean
}): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)

  const onClickWrapper = useCallback(() => {
    setIsLoading(true)
    onClick().then(() => setIsLoading(false))
  }, [onClick])

  return (
    <button
      className={`primary-button ${isLoading ? 'loading' : ''}`}
      disabled={disabled || isLoading}
      onClick={onClickWrapper}
      type={isSubmit ? 'submit' : 'button'}
    >
      {!isLoading ? text : <Spinner message={loadingMessage} />}
    </button>
  )
}
