import cn from 'classnames'
import React from 'react'

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
  const isNewStyles = true
  /* istanbul ignore next: graphic variation */
  const styles = isNewStyles ? newStyles : oldStyles
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
      <span className={styles['border-cut']}>
        {closable && (
          <button onClick={handleOnClick} type="button">jdjdj
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
      </span>
    </div>
  )
}

export default BannerLayout
