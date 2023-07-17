import cn from 'classnames'
import React from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import shadowTipsHelpIcon from 'icons/shadow-tips-help.svg'
import shadowTipsWarningIcon from 'icons/shadow-tips-warning.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BannerLayout.module.scss'

export interface BannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  linkNode?: React.ReactNode | React.ReactNode[]
  type?: 'notification-info' | 'attention' | 'light'
  closable?: boolean
  minimalStyle?: boolean
  handleOnClick?: () => void
  className?: string
  showTitle?: boolean
  isProvider?: boolean
}

const BannerLayout = ({
  children,
  type = 'attention',
  closable = false,
  minimalStyle = false,
  handleOnClick,
  className,
  linkNode,
  showTitle = true,
  isProvider = false,
}: BannerLayoutProps): JSX.Element => {
  return (
    <div
      className={cn(
        styles[`bi-banner`],
        styles[type],
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
              type != 'light' ? (
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
                    [styles['with-margin']]: !!linkNode,
                  },
                  {
                    [styles['provider']]: !!isProvider,
                  }
                )}
              >
                {children}
              </div>
            )}

            {linkNode}
          </div>
        </div>
      </div>
    </div>
  )
}

export default BannerLayout
