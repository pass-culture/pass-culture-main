import cn from 'classnames'
import React from 'react'

import styles from './Title.module.scss'

interface ITitleProps {
  level: 1 | 2 | 3 | 4
  as?: 'p' | 'span' | 'h1' | 'h2' | 'h3' | 'h4'
  className?: string
  children?: React.ReactNode
}

const Title: React.FC<ITitleProps> = ({ level, as, className, children }) => {
  const CustomTag = React.createElement(
    as || `h${level}`,
    { className: cn(styles[`title-${level}`], className) },
    children
  )

  return CustomTag
}

export default Title
