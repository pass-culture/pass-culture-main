import React from 'react'

import { ReactComponent as CloseIcon } from 'assets/close.svg'

import './Tag.scss'

interface TagProps {
  label: string
  onClick: () => void
}

const Tag = ({ label, onClick }: TagProps): JSX.Element => {
  return (
    <div className="tag">
      {label}
      <CloseIcon className="tag-close-icon" onClick={onClick} role="button" />
    </div>
  )
}

export default Tag
