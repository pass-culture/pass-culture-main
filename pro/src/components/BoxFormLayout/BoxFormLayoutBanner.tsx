import cn from 'classnames'
import React from 'react'

import style from './BoxFormLayout.module.scss'

interface BoxFormLayoutBanner {
  className?: string
  banner: React.ReactNode
}

const Banner = ({ className, banner }: BoxFormLayoutBanner): JSX.Element => (
  <div className={cn(style['box-form-layout-banner'], className)}>{banner}</div>
)

export default Banner
