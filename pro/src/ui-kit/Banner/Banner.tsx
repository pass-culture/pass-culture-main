import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'

export interface IBannerProps {
  icon?: string
  href?: string
  linkTitle?: string
  children?: React.ReactNode | React.ReactNode[]
  targetLink?: string
  type?: 'notification-info' | 'attention' | 'light'
  closable?: boolean
  handleOnClick?: () => void
  className?: string
}

const Banner = ({
  icon = 'ico-external-site',
  href,
  linkTitle,
  children,
  targetLink = '_blank',
  type = 'attention',
  closable = false,
  handleOnClick,
  className,
}: IBannerProps): JSX.Element => {
  return (
    <div className={cn('bi-banner', type, className)}>
      {closable && (
        <button onClick={handleOnClick} type="button">
          <Icon alt="Masquer le bandeau" svg="icons-close" />
        </button>
      )}

      <p>{children}</p>

      {href && linkTitle && (
        <p>
          <a
            className="bi-link tertiary-link"
            href={href}
            rel="noopener noreferrer"
            target={targetLink}
          >
            <Icon svg={icon} />
            {linkTitle}
          </a>
        </p>
      )}
    </div>
  )
}

export default Banner
