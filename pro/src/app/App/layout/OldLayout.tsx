import classnames from 'classnames'
import React from 'react'
import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'commons/store/user/selectors'
import { SkipLinks } from 'components/SkipLinks/SkipLinks'
import fullInfoIcon from 'icons/full-info.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OldLayout.module.scss'

interface OldLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading?: string
}

export const OldLayout = ({ children, mainHeading }: OldLayoutProps) => {
  const currentUser = useSelector(selectCurrentUser)
  const renderMainHeading = () => {
    if (!mainHeading) {
      return null
    }

    return <h1 className={styles['main-heading']}>{mainHeading}</h1>
  }

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
      <main
        id="content"
        className={classnames({
          page: true,
          [styles['container-without-nav']]: true,
        })}
      >
        <>
          {renderMainHeading()}
          {children}
        </>
      </main>
    </>
  )
}
