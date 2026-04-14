import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import type { CollectiveOffersVariantMap } from '../types'
import styles from './CollectiveOffersTemplateCard.module.scss'
import { CollectiveOffersTemplateLine } from './components/CollectiveOffersTemplateLine/CollectiveOffersTemplateLine'

type CollectiveOffersTemplateCardProps = {
  offers: CollectiveOffersVariantMap['TEMPLATE'][]
}

export const CollectiveOffersTemplateCard = ({
  offers,
}: CollectiveOffersTemplateCardProps): JSX.Element => {
  return (
    <Card>
      <Card.Header title={'Offres vitrines'} />
      <Card.Content className={styles['offer-list']}>
        {offers.map((offer) => (
          <CollectiveOffersTemplateLine key={offer.id} offer={offer} />
        ))}
      </Card.Content>
      <Card.Footer>
        <Button
          as="a"
          to="/offres/vitrines"
          label="Voir toutes les offres"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
        />
      </Card.Footer>
    </Card>
  )
}
