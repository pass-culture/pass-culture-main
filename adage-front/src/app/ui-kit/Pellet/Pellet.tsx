import cn from 'classnames'
import React from 'react'

import './Pellet.scss'

const Pellet = ({
  label,
  className,
}: {
  label: string | number
  className?: string
}): JSX.Element => <div className={cn('pellet', className)}>{label}</div>

export default Pellet
