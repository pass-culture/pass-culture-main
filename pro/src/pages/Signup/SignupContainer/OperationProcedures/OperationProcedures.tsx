import { useLocation } from 'react-router'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { Callout } from 'ui-kit/Callout/Callout'

import styles from './OperationProcedures.module.scss'

export const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  return (
    <Callout
      links={[
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4411999179665',
          label: 'Consulter notre centre d’aide',
          isExternal: true,
          onClick: () =>
            logEvent(Events.CLICKED_HELP_CENTER, { from: location.pathname }),
        },
      ]}
      className={styles['desk-callout']}
    >
      <p className={styles.description}>
        Nous vous invitons à prendre connaissance des modalités de
        fonctionnement avant de renseigner les champs suivants.
      </p>
    </Callout>
  )
}
