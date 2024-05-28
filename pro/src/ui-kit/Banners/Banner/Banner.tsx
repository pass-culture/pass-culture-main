import cn from 'classnames'
import React from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import shadowTipsHelpIcon from 'icons/shadow-tips-help.svg'
import shadowTipsWarningIcon from 'icons/shadow-tips-warning.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { LinkNodes, Link } from '../LinkNodes/LinkNodes'

import styles from './Banner.module.scss'

export interface BannerProps {
  children?: React.ReactNode | React.ReactNode[]
  links?: Link[]
  type?: 'notification-info' | 'attention' | 'light'
  closable?: boolean
  minimalStyle?: boolean
  handleOnClick?: () => void
  className?: string
  showTitle?: boolean
  isProvider?: boolean
}

export const Banner = ({
  children,
  type = 'attention',
  closable = false,
  minimalStyle = false,
  handleOnClick,
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
        {closable && (
          <button onClick={handleOnClick} type="button">
            {
              /* istanbul ignore next: graphic variation */
              type !== 'light' ? (
                <SvgIcon
                  src={fullClearIcon}
                  alt="Masquer le bandeau"
                  className={cn(styles['close-icon-banner'])}
                />
              ) : (
                <SvgIcon
                  src={strokeCloseIcon}
                  alt="Masquer le bandeau"
                  className={styles['close-icon']}
                />
              )
            }
          </button>
        )}

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
