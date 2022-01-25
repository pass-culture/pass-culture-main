import cn from 'classnames'
import React from 'react'
import './SearchButton.scss'

interface ISearchButton {
  onClick: () => void
  className?: string
  label?: string
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

const SearchButton = ({
  className,
  onClick,
  label,
  disabled = false,
  variant = 'primary',
}: ISearchButton): JSX.Element => {
  return (
    <button
      className={cn('search-button', className, {
        'search-button-primary': variant === 'primary',
        'search-button-secondary': variant === 'secondary',
      })}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  )
}

export default SearchButton
