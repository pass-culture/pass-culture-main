import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'

import styles from './AccessibilityLayout.module.scss'

export interface AccessibilityLayoutProps {
  children?: React.ReactNode
}

export const AccessibilityLayout = ({ children }: AccessibilityLayoutProps) => {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <FullLayout>
      <div className={styles['content-wrapper']}>{children}</div>
    </FullLayout>
  ) : (
    <LoggedOutLayout>
      <section className={styles['layout']} data-testid="logged-out-section">
        <div className={styles['content']}>{children}</div>
      </section>
    </LoggedOutLayout>
  )
}
