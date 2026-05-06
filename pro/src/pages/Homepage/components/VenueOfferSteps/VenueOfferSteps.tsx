import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'
import { Panel } from '@/ui-kit/Panel/Panel'

import styles from './VenueOfferSteps.module.scss'

export const VenueOfferSteps = () => {
  const { logEvent } = useAnalytics()

  return (
    <Panel>
      <div className={styles['card-wrapper']}>
        <h3 className={styles['card-title']}>Prochaines étapes : </h3>

        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          iconPosition={IconPositionEnum.LEFT}
          icon={fullNextIcon}
          to={`/partenaire/page-collective`}
          label="Renseigner mes informations à destination des enseignants"
        />

        <h3 className={styles['card-title']}>Démarche en cours : </h3>

        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          iconPosition={IconPositionEnum.LEFT}
          icon={fullNextIcon}
          to={`/partenaire/page-collective`}
          onClick={() => {
            logEvent(Events.CLICKED_EAC_DMS_TIMELINE, {
              from: location.pathname,
            })
          }}
          label="Suivre ma demande de référencement ADAGE"
        />
      </div>
    </Panel>
  )
}
