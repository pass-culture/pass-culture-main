import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import type {
  CollectiveOffersCardVariant,
  CollectiveOffersVariantMap,
} from '../types'
import styles from './CollectiveOffersBookableCard.module.scss'
import { CollectiveOffersBookableLine } from './components/CollectiveOffersBookableLine/CollectiveOffersBookableLine'

type CollectiveOffersBookableCardProps = {
  offers: CollectiveOffersVariantMap[CollectiveOffersCardVariant.BOOKABLE][]
}

export const CollectiveOffersBookableCard = ({
  offers,
}: CollectiveOffersBookableCardProps): JSX.Element => {
  return (
    <Card>
      <Card.Header title={'Offres réservables'} />
      <Card.Content className={styles['offer-list']}>
        {offers.map((offer) => (
          <CollectiveOffersBookableLine key={offer.id} offer={offer} />
        ))}
      </Card.Content>
      <Card.Footer>
        <Button
          as="a"
          to="/offres/collectives"
          label="Voir toutes les offres"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
        />
      </Card.Footer>
    </Card>
  )
}
