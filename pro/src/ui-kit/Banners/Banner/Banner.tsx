import cn from 'classnames'
import React from 'react'

import shadowTipsHelpIcon from 'icons/shadow-tips-help.svg'
import shadowTipsWarningIcon from 'icons/shadow-tips-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { LinkNodes, Link } from '../LinkNodes/LinkNodes'

import styles from './Banner.module.scss'

export interface BannerProps {
  children?: React.ReactNode | React.ReactNode[]
  links?: Link[]
  type?: 'notification-info' | 'attention' | 'light'
  minimalStyle?: boolean
  handleOnClick?: () => void
  className?: string
  showTitle?: boolean
  isProvider?: boolean
}

export const Banner = ({
  children,
  type = 'attention',
  minimalStyle = false,
  className,
  links,
  showTitle = true,
  isProvider = false,
}: BannerProps): JSX.Element => {
  return (
    <div
      className={cn(
        styles[`bi-banner`],
        styles[type],
        /* istanbul ignore next: graphic variation */
        minimalStyle && styles['is-minimal'],
        showTitle && styles['title'],
        className
      )}
    >
      {type === 'notification-info' && showTitle && (
        <div className={styles['container']}>
          <SvgIcon
            src={shadowTipsHelpIcon}
            alt=""
            className={styles['icon']}
            width="24"
          />
          <span className={styles['container-title']}>À SAVOIR</span>
        </div>
      )}
      {type === 'attention' && showTitle && (
        <div className={styles['container']}>
          <SvgIcon
            src={shadowTipsWarningIcon}
            alt=""
            className={styles['icon']}
            width="24"
          />
          <span className={styles['container-title']}>IMPORTANT</span>
        </div>
      )}
      <div className={styles['border-cut']}>
        <div className={styles['content']}>
          <div>
            {children && (
              <div
                className={cn(
                  styles['bi-banner-text'],
                  {
                    [styles['with-margin']]: !!links,
                  },
                  {
                    [styles['provider']]: !!isProvider,
                  }
                )}
              >
                {children}
              </div>
            )}

            <LinkNodes links={links} />
          </div>
        </div>
      </div>
    </div>
  )
}
