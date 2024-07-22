import classnames from 'classnames'
import React from 'react'
import { useSelector } from 'react-redux'

import { Footer } from 'components/Footer/Footer'
import { OldHeader } from 'components/Header/OldHeader'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import fullInfoIcon from 'icons/full-info.svg'
import { selectCurrentUser } from 'store/user/selectors'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OldLayout.module.scss'

interface OldLayoutProps {
  children?: React.ReactNode
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const OldLayout = ({ children, layout = 'basic' }: OldLayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    <>
      <SkipLinks />
      {currentUser?.isImpersonated && (
        <aside className={styles['connect-as']}>
          <SvgIcon
            src={fullInfoIcon}
            alt="Information"
            width="20"
            className={styles['connect-as-icon']}
          />
          <div className={styles['connect-as-text']}>
            Vous êtes connecté en tant que :&nbsp;
            <strong>
              {currentUser.firstName} {currentUser.lastName}
            </strong>
          </div>
        </aside>
      )}
      {(layout === 'basic' || layout === 'sticky-actions') && <OldHeader />}

      <main
        id="content"
        className={classnames({
          page: true,
          [styles['container'] ?? '']:
            layout === 'basic' || layout === 'sticky-actions',
          [styles['container-sticky-actions'] ?? '']:
            layout === 'sticky-actions',
          [styles['container-without-nav'] ?? '']: layout === 'without-nav',
        })}
      >
        {layout === 'funnel' || layout === 'without-nav' ? (
          children
        ) : (
          <div className={styles['page-content']}>
            <div className={styles['after-notification-content']}>
              {children}
            </div>
          </div>
        )}
      </main>
      {layout !== 'funnel' && <Footer layout={layout} />}
    </>
  )
}
