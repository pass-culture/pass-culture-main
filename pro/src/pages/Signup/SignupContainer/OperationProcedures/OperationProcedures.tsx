import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './OperationProcedures.module.scss'

export const OperatingProcedures = (): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  return (
    <div className={styles['desk-callout']}>
      <Banner
        title=""
        actions={[
          {
            href: 'https://passculture.zendesk.com/hc/fr/articles/4411999179665',
            label: 'Consulter notre centre d’aide',
            isExternal: true,
            icon: fullLinkIcon,
            iconAlt: 'Nouvelle fenêtre',
            type: 'link',
            onClick: () =>
              logEvent(Events.CLICKED_HELP_CENTER, { from: location.pathname }),
          },
        ]}
        description={
          <p className={styles.description}>
            Nous vous invitons à prendre connaissance des modalités de
            fonctionnement avant de renseigner les champs suivants.
          </p>
        }
      />
    </div>
  )
}
