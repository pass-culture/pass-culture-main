import React from 'react'
import { useLocation } from 'react-router-dom'

import Callout from 'components/Callout/Callout'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullLinkIcon from 'icons/full-link.svg'

import styles from './OperationProcedures.module.scss'

const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  return (
    <Callout
      links={[
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4411999179665',
          linkTitle: 'Consulter notre centre d’aide',
          isExternal: true,
          onClick: () =>
            logEvent?.(Events.CLICKED_HELP_CENTER, { from: location.pathname }),
          icon: fullLinkIcon,
          svgAlt: 'Nouvelle fenêtre',
        },
      ]}
    >
      <p className={styles.description}>
        Nous vous invitons à prendre connaissance des modalités de
        fonctionnement avant de renseigner les champs suivants.
      </p>
    </Callout>
  )
}

export default OperatingProcedures
