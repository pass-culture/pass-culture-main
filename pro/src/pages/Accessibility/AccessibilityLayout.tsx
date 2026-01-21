import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import styles from './AccessibilityLayout.module.scss'

export interface AccessibilityLayoutProps {
  children?: React.ReactNode
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
  showBackToSignInButton?: boolean
}

export const AccessibilityLayout = ({
  children,
  mainHeading,
  showBackToSignInButton,
}: AccessibilityLayoutProps) => {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <BasicLayout mainHeading={mainHeading}>{children}</BasicLayout>
  ) : (
    <LoggedOutLayout mainHeading={mainHeading}>
      <section className={styles['layout']} data-testid="logged-out-section">
        <div className={styles['content']}>{children}</div>
        {showBackToSignInButton && (
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="connexion"
            icon={fullBackIcon}
            className={styles['back-to-signin-button']}
          >
            Retour à la page de connexion
          </Button>
        )}
      </section>
    </LoggedOutLayout>
  )
}
