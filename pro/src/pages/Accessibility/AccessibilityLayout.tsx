import { AppLayout } from 'app/AppLayout'
import { useCurrentUser } from 'hooks/useCurrentUser'
import fullBackIcon from 'icons/full-back.svg'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AccessibilityLayout.module.scss'

export const AccessibilityLayout = ({
  children,
  showBackToSignInButton,
}: {
  children?: React.ReactNode
  showBackToSignInButton?: boolean
}) => {
  let isUserConnected = false
  try {
    const user = useCurrentUser()
    isUserConnected = Boolean(user)
  } catch (e) {
    isUserConnected = false
  }

  return isUserConnected ? (
    <AppLayout>{children}</AppLayout>
  ) : (
    <AppLayout layout="without-nav">
      <header className={styles['logo-side']}>
        <SvgIcon
          className="logo-unlogged"
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l’espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
      <section className={styles['layout']}>
        <div className={styles['content']}>{children}</div>
        {showBackToSignInButton && (
          <ButtonLink
            link={{ to: 'connexion' }}
            icon={fullBackIcon}
            className={styles['back-to-signin-button']}
          >
            Retour à la page de connexion
          </ButtonLink>
        )}
      </section>
    </AppLayout>
  )
}
