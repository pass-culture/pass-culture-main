import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as IcoClearIcon } from 'icons/ico-clear.svg'
import { ReactComponent as CloseIcon } from 'icons/icons-close.svg'

import oldStyles from './BannerLayout.module.scss'
import newStyles from './NewBannerLayout.module.scss'

export interface IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  linkNode?: React.ReactNode | React.ReactNode[]
  type?: 'notification-info' | 'attention' | 'light' | 'new'
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
  const isNewStyles = false
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
      <span className={styles['border-cut']}>
        {closable && (
          <button onClick={handleOnClick} type="button">
            {isNewStyles && type != 'new' && type != 'light' ? (
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
