import cn from 'classnames'

import style from '../BoxFormLayout.module.scss'

interface BoxFormLayoutBanner {
  className?: string
  banner: React.ReactNode
}

export const Banner = ({
  className,
  banner,
}: BoxFormLayoutBanner): JSX.Element => (
  <div className={cn(style['box-form-layout-banner'], className)}>{banner}</div>
)
