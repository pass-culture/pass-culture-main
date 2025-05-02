import cn from 'classnames'
import { useLocation } from 'react-router'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import fullLinkIcon from 'icons/full-link.svg'
import fullMailIcon from 'icons/full-mail.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './LegalInfos.module.scss'

interface LegalInfoProps {
  title: string
  className: string
}

export const LegalInfos = ({
  title,
  className,
}: LegalInfoProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  const DPOMail = 'dpo@passculture.app'

  const componentData = isNewSignupEnabled ? (
    <Callout
      variant={CalloutVariant.DEFAULT}
      className={cn(styles['legal-infos-callout'], className)}
    >
      <p className={styles['legal-infos-paragraph']}>
        En cliquant sur S’inscrire, vous acceptez nos{' '}
        <ButtonLink
          variant={ButtonVariant.QUATERNARY}
          icon={fullLinkIcon}
          className={styles['legal-infos-callout-link']}
          opensInNewTab
          onClick={() =>
            logEvent(Events.CLICKED_CONSULT_CGU, { from: location.pathname })
          }
          to="https://pass.culture.fr/cgu-professionnels/"
        >
          Conditions générales d’utilisation.
        </ButtonLink>
      </p>
      <p className={styles['legal-infos-paragraph']}>
        Pour la gestion de vos données personnelles par la SAS pass Culture,
        vous pouvez consulter la charte des données personnelles ou contacter{' '}
        <ButtonLink
          variant={ButtonVariant.QUATERNARY}
          icon={fullLinkIcon}
          className={styles['legal-infos-callout-maillink']}
          to={`mailto:${DPOMail}`}
          isExternal
        >
          {DPOMail}
        </ButtonLink>
        .
      </p>
    </Callout>
  ) : (
    <div className={cn(styles['legal-infos'], className)}>
      <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
      <ButtonLink
        className={styles['quaternary-link']}
        onClick={() =>
          logEvent(Events.CLICKED_CONSULT_CGU, { from: location.pathname })
        }
        to="https://pass.culture.fr/cgu-professionnels/"
        isExternal
        opensInNewTab
        variant={ButtonVariant.QUATERNARY}
      >
        Conditions Générales d’Utilisation
      </ButtonLink>
      <span>{' ainsi que notre '}</span>
      <ButtonLink
        className={styles['quaternary-link']}
        onClick={() =>
          logEvent(Events.CLICKED_PERSONAL_DATA, { from: location.pathname })
        }
        to="https://pass.culture.fr/donnees-personnelles/"
        isExternal
        opensInNewTab
        variant={ButtonVariant.QUATERNARY}
      >
        Charte des Données Personnelles
      </ButtonLink>
      <span>
        {
          '. Pour en savoir plus sur la gestion de vos données personnelles et pour exercer vos droits, ou répondre à toute autre question, '
        }
      </span>
      <ButtonLink
        className={styles['quaternary-link']}
        variant={ButtonVariant.QUATERNARY}
        onClick={() =>
          logEvent(Events.CLICKED_CONSULT_SUPPORT, {
            from: location.pathname,
          })
        }
        to="mailto:support-pro@passculture.app"
        isExternal
      >
        <SvgIcon
          src={fullMailIcon}
          alt=""
          className={styles['icon-legal-infos']}
          width="22"
        />
        Contacter notre support par mail à{' '}
        <span className={styles['legal-infos-support-email']}>
          support-pro@passculture.app
        </span>
      </ButtonLink>
      .
    </div>
  )

  return componentData
}
