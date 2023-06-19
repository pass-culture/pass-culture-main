import React from 'react'
import { useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullExternalIcon from 'icons/full-external-site.svg'
import Banner from 'ui-kit/Banners/Banner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OperationProcedures.module.scss'

const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  return (
    <Banner type={'notification-info'}>
      <p className={styles.description}>
        Nous vous invitons à prendre connaissance des modalités de
        fonctionnement avant de renseigner les champs suivants.
      </p>
      <a
        className="tertiary-link"
        href="https://passculture.zendesk.com/hc/fr/articles/4411999179665"
        onClick={() =>
          logEvent?.(Events.CLICKED_HELP_CENTER, { from: location.pathname })
        }
        rel="noopener noreferrer"
        target="_blank"
      >
        <SvgIcon
          src={fullExternalIcon}
          alt="Site aide.passculture.app"
          className={styles.icon}
        />
        <span>Consulter notre centre d’aide</span>
      </a>
    </Banner>
  )
}

export default OperatingProcedures
