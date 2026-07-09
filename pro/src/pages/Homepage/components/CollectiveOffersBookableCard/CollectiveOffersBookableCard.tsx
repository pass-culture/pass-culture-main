import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import styles from '../CollectiveOffersList.module.scss'
import { OffersCardVariant } from '../types'
import { CollectiveOffersBookableLine } from './components/CollectiveOffersBookableLine/CollectiveOffersBookableLine'

export interface CollectiveOffersBookableCardProps {
  isReadOnly: boolean
  offers: CollectiveOfferHomeResponseModel[]
}

export const CollectiveOffersBookableCard = ({
  isReadOnly,
  offers,
}: Readonly<CollectiveOffersBookableCardProps>) => {
  const { logEvent } = useAnalytics()
  const logSeeAllOffersClick = () =>
    logEvent(HomepageEvents.CLICKED_SEE_ALL_OFFERS, {
      offersVariant: OffersCardVariant.BOOKABLE,
      hasOffersDisplayed: true,
    })

  return (
    <Card>
      <Card.Header title={'Offres réservables'} />
      <Card.Content className={styles['offer-list']}>
        {offers.map((offer) => (
          <CollectiveOffersBookableLine
            key={offer.id}
            isReadOnly={isReadOnly}
            offer={offer}
          />
        ))}
      </Card.Content>
      <Card.Footer>
        <Button
          as="a"
          to="/offres/collectives"
          label="Voir toutes les offres"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={logSeeAllOffersClick}
        />
      </Card.Footer>
    </Card>
  )
}
