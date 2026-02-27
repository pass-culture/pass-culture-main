import { Panel } from '@/ui-kit/Panel/Panel'

import { CollectiveAdagePendingStatus } from './CollectiveAdagePendingStatus'
import styles from './CollectiveDmsTimeline.module.scss'
import { CollectiveDmsTimelineVariant } from './types'

export const OngoingDmsApplicationWrapper = ({
  children,
  variant,
}: {
  children: React.ReactNode
  variant?: CollectiveDmsTimelineVariant
}) => {
  if (variant === CollectiveDmsTimelineVariant.LITE) {
    return (
      <Panel>
        <h2 className={styles['panel-title']}>
          État d’avancement de votre dossier
        </h2>
        <CollectiveAdagePendingStatus />
        {children}
      </Panel>
    )
  }
  return <>{children}</>
}
