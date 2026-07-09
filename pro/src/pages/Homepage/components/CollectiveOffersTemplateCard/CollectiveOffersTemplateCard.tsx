import type { CollectiveOfferTemplateHomeResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import styles from '../CollectiveOffersList.module.scss'
import { OffersCardVariant } from '../types'
import { CollectiveOffersTemplateLine } from './components/CollectiveOffersTemplateLine/CollectiveOffersTemplateLine'

interface CollectiveOffersTemplateCardProps {
  isReadOnly: boolean
  offers: CollectiveOfferTemplateHomeResponseModel[]
}

export const CollectiveOffersTemplateCard = ({
  isReadOnly,
  offers,
}: Readonly<CollectiveOffersTemplateCardProps>) => {
  const { logEvent } = useAnalytics()

  const logSeeAllOffersClick = () =>
    logEvent(HomepageEvents.CLICKED_SEE_ALL_OFFERS, {
      offersVariant: OffersCardVariant.TEMPLATE,
      hasOffersDisplayed: true,
    })

  return (
    <Card>
      <Card.Header title={'Offres vitrines'} />
      <Card.Content className={styles['offer-list']}>
        {offers.map((offer) => (
          <CollectiveOffersTemplateLine
            key={offer.id}
            isReadOnly={isReadOnly}
            offer={offer}
          />
        ))}
      </Card.Content>
      <Card.Footer>
        <Button
          as="a"
          to="/offres/vitrines"
          label="Voir toutes les offres"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={logSeeAllOffersClick}
        />
      </Card.Footer>
    </Card>
  )
}
