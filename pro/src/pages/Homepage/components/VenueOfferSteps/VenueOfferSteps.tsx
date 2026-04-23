import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
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
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

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
          to={`/structures/${selectedPartnerVenue.managingOfferer.id}/lieux/${selectedPartnerVenue.id}/collectif`}
          label="Renseigner mes informations à destination des enseignants"
        />

        <h3 className={styles['card-title']}>Démarche en cours : </h3>

        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          iconPosition={IconPositionEnum.LEFT}
          icon={fullNextIcon}
          to={`/structures/${selectedPartnerVenue.managingOfferer.id}/lieux/${selectedPartnerVenue.id}/collectif`}
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
