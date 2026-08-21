import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'

import styles from './AccessibilityLayout.module.scss'

export interface AccessibilityLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
}

export const AccessibilityLayout = ({
  children,
  mainHeading,
}: AccessibilityLayoutProps) => {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <FullLayout>
      <div className={styles['content-wrapper']}>
        <MainHeading mainHeading={mainHeading} />
        {children}
      </div>
    </FullLayout>
  ) : (
    <LoggedOutLayout mainHeading={mainHeading}>
      <section className={styles['layout']} data-testid="logged-out-section">
        <div className={styles['content']}>{children}</div>
      </section>
    </LoggedOutLayout>
  )
}
