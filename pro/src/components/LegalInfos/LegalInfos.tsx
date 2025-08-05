import cn from 'classnames'
import { useLocation } from 'react-router'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'

import styles from './LegalInfos.module.scss'

interface LegalInfoProps {
  className: string
}

export const LegalInfos = ({ className }: LegalInfoProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  const DPOMail = 'dpo@passculture.app'

  return (
    <Callout className={cn(styles['legal-infos-callout'], className)}>
      <p className={styles['legal-infos-paragraph']}>
        En cliquant sur S’inscrire, vous acceptez nos{' '}
        <ButtonLink
          variant={ButtonVariant.QUATERNARY}
          icon={fullLinkIcon}
          className={styles['legal-infos-callout-link']}
          opensInNewTab
          isExternal
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
          className={styles['legal-infos-callout-link']}
          to={`mailto:${DPOMail}`}
          isExternal
        >
          {DPOMail}
        </ButtonLink>
        .
      </p>
    </Callout>
  )
}
