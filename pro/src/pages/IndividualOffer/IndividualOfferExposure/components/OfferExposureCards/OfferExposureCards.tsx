import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  ExposureEventType,
  type GetIndividualOfferResponseModelV2,
} from '@/apiClient/v1'
import { GET_OFFER_EXPOSURE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { formatCount } from '@/commons/format/formatCount'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullArrowRightIcon from '@/icons/full-arrow-right.svg'
import fullIncrease from '@/icons/full-increase.svg'
import strokeEventIcon from '@/icons/stroke-events.svg'
import strokeShowIcon from '@/icons/stroke-show.svg'
import { Card } from '@/ui-kit/Card/Card'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { isOngoing } from '../../commons/utils'
import styles from './OfferExposureCards.module.scss'

const getEventLabel = (eventType?: ExposureEventType): string => {
  switch (eventType) {
    case ExposureEventType.HEADLINE:
      return 'la mise à la une'
    case ExposureEventType.HIGHLIGHT:
      return `le début du temps fort`
    case ExposureEventType.PRO_ADVICE:
      return 'l’ajout d’une recommandation'
    // This should not happen
    default:
      return 'un événement de mise en avant'
  }
}

const SIX_MONTHS = 180 * 24 * 60 * 60 * 1000

export type OfferExposureCardsProps = {
  offer: GetIndividualOfferResponseModelV2
}
export const OfferExposureCards = ({
  offer,
}: Readonly<OfferExposureCardsProps>) => {
  const { data: exposure } = useSWR(
    [GET_OFFER_EXPOSURE_QUERY_KEY, offer.id],
    () => api.getOfferExposure({ path: { offer_id: offer.id } })
  )

  const isEnhancementOngoing =
    !!exposure?.events[0]?.viewsOnPeriod && isOngoing(exposure?.events[0])

  const isMoreThanSixMonthsSinceCreation =
    new Date(offer.dateCreated) < new Date(Date.now() - SIX_MONTHS)

  return (
    <>
      <h2 className={styles['title']}>Statistiques de votre offre</h2>
      <div className={styles['exposure-container']}>
        <Card className={styles['card']}>
          <Card.Header
            titleTag="p"
            title={`${formatCount(exposure?.views ?? 0)} ${pluralizeFr(exposure?.views ?? 0, 'consultation', 'consultations')}`}
            subtitle={
              isMoreThanSixMonthsSinceCreation
                ? 'sur les 6 derniers mois'
                : 'depuis la publication de l’offre'
            }
            icon={strokeShowIcon}
          />
          <Card.Content>
            {isEnhancementOngoing && (
              <div className={styles['lifted-views']}>
                <SvgIcon
                  src={fullIncrease}
                  alt=""
                  width="16"
                  className={styles['lifted-views-icon']}
                />
                <p
                  className={styles['lifted-views-text']}
                >{`+${formatCount(exposure?.events[0].viewsOnPeriod ?? 0)} depuis ${getEventLabel(exposure?.events[0].type)}`}</p>
              </div>
            )}
          </Card.Content>
        </Card>

        <Card className={styles['card']}>
          <Card.Header
            titleTag="p"
            title={`${new Intl.NumberFormat('fr-FR').format(offer.bookingsCount ?? 0)} ${pluralizeFr(offer.bookingsCount ?? 0, 'réservation', 'réservations')}`}
            subtitle="depuis la publication de l’offre"
            icon={strokeEventIcon}
          />
          <Card.Content>
            <div className={styles['bookings-button']}>
              <Button
                as="a"
                to={`${getIndividualOfferUrl({
                  offerId: offer.id,
                  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                })}`}
                label="Voir les réservations"
                variant={ButtonVariant.TERTIARY}
                icon={fullArrowRightIcon}
                iconPosition={IconPositionEnum.LEFT}
                size={ButtonSize.SMALL}
              />
            </div>
          </Card.Content>
        </Card>
      </div>
    </>
  )
}
