import React from 'react'
import './SearchButton.scss'

interface ISearchButton {
  onClick: () => void
  className?: string
  label?: string
}

const SearchButton = ({
  className,
  onClick,
  label,
}: ISearchButton): JSX.Element => {
  return (
    <button
      className={`search-button ${className}`}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  )
}

export default SearchButton
