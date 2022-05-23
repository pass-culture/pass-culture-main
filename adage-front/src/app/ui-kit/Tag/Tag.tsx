import cn from 'classnames'
import React from 'react'

import { ReactComponent as CloseIcon } from 'assets/close.svg'

import './Tag.scss'

interface TagProps {
  label: string
  onClick?: () => void
}

const Tag = ({ label, onClick }: TagProps): JSX.Element => {
  return (
    <div className={cn('tag', { ['with-hover']: Boolean(onClick) })}>
      {label}
      {onClick && (
        <CloseIcon className="tag-close-icon" onClick={onClick} role="button" />
      )}
    </div>
  )
}

export default Tag
