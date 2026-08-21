import type React from 'react'

import {
  Header,
  type HeaderProps,
} from '@/app/App/layouts/components/Header/Header'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'

import { Footer } from '../components/Footer/Footer'
import styles from './FullLayout.module.scss'

type FullLayoutProps = {
  children: React.ReactNode
  headerPropsOverride?: HeaderProps
}

export const FullLayout = ({
  children,
  headerPropsOverride,
}: Readonly<FullLayoutProps>): JSX.Element => {
  const currentUser = useAppSelector(selectCurrentUser)

  const isUnauthenticated = currentUser === null

  return (
    <div className={styles.layout}>
      <SkipLinks />
      <Header
        isUnauthenticated={isUnauthenticated}
        hideAdminButton={true}
        disableBurgerMenu
        forceShowHelpCenter
        {...headerPropsOverride}
      />
      <main id="content" className={styles.content} tabIndex={-1}>
        {children}
      </main>
      <Footer isUnauthenticated={isUnauthenticated} />
    </div>
  )
}
