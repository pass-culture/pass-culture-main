import React from 'react'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  className?: string
  hasError?: boolean
  filterVariant?: boolean
  rightIcon?: () => JSX.Element | null
  rightButton?: () => JSX.Element
}

const BaseInput = ({
  className,
  hasError,
  filterVariant,
  name,
  rightIcon,
  rightButton,
  ...props
}: IBaseInputProps) => {
  return null
}

export default BaseInput
