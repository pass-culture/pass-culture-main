import { useSelector } from 'react-redux'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import fullBackIcon from '@/icons/full-back.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'

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
  const user = useSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <BasicLayout mainHeading={mainHeading}>{children}</BasicLayout>
  ) : (
    <LoggedOutLayout mainHeading={mainHeading}>
      <section className={styles['layout']} data-testid="logged-out-section">
        <div className={styles['content']}>{children}</div>
        {showBackToSignInButton && (
          <ButtonLink
            to="connexion"
            icon={fullBackIcon}
            className={styles['back-to-signin-button']}
          >
            Retour à la page de connexion
          </ButtonLink>
        )}
      </section>
    </LoggedOutLayout>
  )
}
