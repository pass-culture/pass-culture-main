import { Layout, LayoutProps } from 'app/App/layout/Layout'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import fullBackIcon from 'icons/full-back.svg'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import logoStyles from 'styles/components/_Logo.module.scss'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AccessibilityLayout.module.scss'

interface AccessibilityLayoutProps extends LayoutProps {
  showBackToSignInButton?: boolean
}

export const AccessibilityLayout = ({
  children,
  showBackToSignInButton,
  mainHeading,
}: AccessibilityLayoutProps) => {
  let isUserConnected = false
  try {
    const user = useCurrentUser()
    isUserConnected = Boolean(user)
  } catch {
    isUserConnected = false
  }

  return isUserConnected ? (
    <Layout mainHeading={mainHeading}>{children}</Layout>
  ) : (
    <Layout mainHeading={mainHeading} layout="without-nav">
      <header className={styles['logo-side']}>
        <SvgIcon
          className={logoStyles['logo-unlogged']}
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l’espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
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
