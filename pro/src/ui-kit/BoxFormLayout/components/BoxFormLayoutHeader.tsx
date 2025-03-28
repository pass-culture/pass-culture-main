import cn from 'classnames'

import style from '../BoxFormLayout.module.scss'

interface BoxFormLayoutHeader {
  className?: string
  subtitle: string
  title: string
}

export const Header = ({
  className,
  subtitle,
  title,
}: BoxFormLayoutHeader): JSX.Element => (
  <div className={cn(style['box-form-layout-header'], className)}>
    <div className={style['box-form-layout-header-title']}>{title}</div>
    <div className={style['box-form-layout-header-subtitle']}>{subtitle}</div>
  </div>
)
