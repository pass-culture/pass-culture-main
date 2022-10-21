import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as AttentionIcon } from 'icons/ico-attention.svg'
import { ReactComponent as BulbIcon } from 'icons/ico-bulb.svg'
import { ReactComponent as IcoClearIcon } from 'icons/ico-clear.svg'
import { ReactComponent as CloseIcon } from 'icons/icons-close.svg'

import oldStyles from './BannerLayout.module.scss'
import newStyles from './NewBannerLayout.module.scss'

export interface IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  linkNode?: React.ReactNode | React.ReactNode[]
  type?: 'notification-info' | 'attention' | 'light' | 'new' | 'image'
  closable?: boolean
  minimalStyle?: boolean
  handleOnClick?: () => void
  className?: string
}

const BannerLayout = ({
  children,
  type = 'attention',
  closable = false,
  minimalStyle = false,
  handleOnClick,
  className,
  linkNode,
}: IBannerLayoutProps): JSX.Element => {
  const isNewStyles = true
  const styles = isNewStyles ? newStyles : oldStyles
  return (
    <div
      className={cn(
        styles[`bi-banner`],
        styles[type],
        minimalStyle && styles['is-minimal'],
        className
      )}
    >
      {type === 'notification-info' && <BulbIcon className={styles['icon']} />}
      {type === 'attention' && <AttentionIcon className={styles['icon']} />}
      <span className={styles['border-cut']}>
        {closable && (
          <button onClick={handleOnClick} type="button">
            {isNewStyles &&
            type != 'new' &&
            type != 'light' &&
            type != 'image' ? (
              <IcoClearIcon
                title="Masquer le bandeau"
                className={cn(styles['close-icon-banner'])}
              />
            ) : (
              <CloseIcon
                title="Masquer le bandeau"
                className={styles['close-icon']}
              />
            )}
          </button>
        )}

        <div className={styles['content']}>
          {type === 'new' && (
            <Icon svg="ico-star" className={styles['ico-new']} />
          )}
          <div>
            {children && (
              <div
                className={cn(styles['bi-banner-text'], {
                  [styles['with-margin']]: !!linkNode,
                })}
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
