import cn from 'classnames'
import React from 'react'

import { ReactComponent as CloseIcon } from 'icons/close-dialog.svg'
import { ReactComponent as AttentionIcon } from 'icons/ico-attention.svg'
import { ReactComponent as BulbIcon } from 'icons/ico-bulb.svg'
import { ReactComponent as IcoClearIcon } from 'icons/ico-clear.svg'
import Icon from 'ui-kit/Icon/Icon'

import styles from './BannerLayout.module.scss'

export interface IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  linkNode?: React.ReactNode | React.ReactNode[]
  type?: 'notification-info' | 'attention' | 'light' | 'new' | 'image'
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
}: IBannerLayoutProps): JSX.Element => {
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
        <BulbIcon className={styles['icon']} />
      )}
      {type === 'attention' && showTitle && (
        <AttentionIcon className={styles['icon']} />
      )}
      <span className={styles['border-cut']}>
        {closable && (
          <button onClick={handleOnClick} type="button">
            {
              /* istanbul ignore next: graphic variation */
              type != 'new' && type != 'light' && type != 'image' ? (
                <IcoClearIcon
                  title="Masquer le bandeau"
                  className={cn(styles['close-icon-banner'])}
                />
              ) : (
                <CloseIcon
                  title="Masquer le bandeau"
                  className={styles['close-icon']}
                />
              )
            }
          </button>
        )}

        <div className={styles['content']}>
          {
            /* istanbul ignore next: graphic variation */
            type === 'new' && (
              <Icon svg="ico-star" className={styles['ico-new']} />
            )
          }
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
      </span>
    </div>
  )
}

export default BannerLayout
