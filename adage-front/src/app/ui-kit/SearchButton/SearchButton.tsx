import cn from 'classnames'
import React from 'react'
import './SearchButton.scss'

interface ISearchButton {
  onClick: () => void
  className?: string
  label?: string
  disabled?: boolean
}

const SearchButton = ({
  className,
  onClick,
  label,
  disabled = false,
}: ISearchButton): JSX.Element => {
  return (
    <button
      className={cn('search-button', className)}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  )
}

export default SearchButton
