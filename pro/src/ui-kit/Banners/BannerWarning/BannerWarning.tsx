import cn from 'classnames'
import React from 'react'

import fullNextIcon from 'icons/full-next.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Link } from '../Banner'
import LinkNodes from '../LinkNodes/LinkNodes'

import styles from './BannerWarning.module.scss'

export interface BannerWarningProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
  title: string
  links?: Link[]
}

const BannerWarning = ({
  children,
  className,
  title,
  links,
}: BannerWarningProps): JSX.Element => {
  return (
    <div className={cn(styles['banner'], className)}>
      <SvgIcon
        src={strokeWarningIcon}
        alt=""
        className={styles['icon']}
        width="20"
      />
      <div className={styles['content']}>
        <div className={styles['title']}>{title}</div>
        {children && <div className={styles['banner-text']}>{children}</div>}
        <LinkNodes links={links} defaultLinkIcon={fullNextIcon} />
      </div>
    </div>
  )
}

export default BannerWarning
