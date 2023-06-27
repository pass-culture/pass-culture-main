import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutHeader {
  className?: string
  subtitle: string
  title: string
}

const Header = ({
  className,
  subtitle,
  title,
}: BoxFormLayoutHeader): JSX.Element => (
  <div className={cn(style['box-form-layout-header'], className)}>
    <div className={style['box-form-layout-header-title']}>{title}</div>
    <div className={style['box-form-layout-header-subtitle']}>{subtitle}</div>
  </div>
)

export default Header
