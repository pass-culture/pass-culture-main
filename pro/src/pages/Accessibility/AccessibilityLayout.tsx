import { useSelector } from 'react-redux'

import { Layout, LayoutProps } from '@/app/App/layout/Layout'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import fullBackIcon from '@/icons/full-back.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'

import styles from './AccessibilityLayout.module.scss'

export interface AccessibilityLayoutProps extends LayoutProps {
  showBackToSignInButton?: boolean
}

export const AccessibilityLayout = ({
  children,
  showBackToSignInButton,
  mainHeading,
}: AccessibilityLayoutProps) => {
  const user = useSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <Layout mainHeading={mainHeading} layout="basic">
      {children}
    </Layout>
  ) : (
    <Layout mainHeading={mainHeading} layout="logged-out">
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
    </Layout>
  )
}
