import cn from 'classnames'
import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import fullLink from 'icons/full-link.svg'
import fullMailIcon from 'icons/full-mail.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
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
  return (
    <div className={cn(styles['legal-infos'], className)}>
      <span>{`En cliquant sur ${title}, vous acceptez nos `}</span>
      <ButtonLink
        className={styles['quaternary-link']}
        onClick={() =>
          logEvent(Events.CLICKED_CONSULT_CGU, { from: location.pathname })
        }
        link={{
          to: 'https://pass.culture.fr/cgu-professionnels/',
          isExternal: true,
          target: '_blank',
        }}
        variant={ButtonVariant.QUATERNARY}
      >
        <SvgIcon
          src={fullLink}
          alt="Site pass.culture.fr (Nouvelle fenêtre)"
          className={styles['icon-legal-infos']}
          width="22"
        />
        <span>Conditions Générales d’Utilisation</span>
      </ButtonLink>
      <span>{' ainsi que notre '}</span>
      <ButtonLink
        className={styles['quaternary-link']}
        onClick={() =>
          logEvent(Events.CLICKED_PERSONAL_DATA, { from: location.pathname })
        }
        link={{
          to: 'https://pass.culture.fr/donnees-personnelles/',
          isExternal: true,
          target: '_blank',
        }}
        variant={ButtonVariant.QUATERNARY}
      >
        <SvgIcon
          src={fullLink}
          alt="Site pass.culture.fr (Nouvelle fenêtre)"
          className={styles['icon-legal-infos']}
          width="22"
        />
        <span>Charte des Données Personnelles</span>
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
        link={{
          to: 'mailto:support-pro@passculture.app',
          isExternal: true,
          target: '_blank',
        }}
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
}
