import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_OFFERS_HOME_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import { OffersRetentionCard } from '../OffersRetentionCard/OffersRetentionCard'
import { IndividualOffersLine } from './components/IndividualOffersLine/IndividualOffersLine'
import styles from './IndividualOffersCard.module.scss'

type IndividualOffersCardProps = {
  venueId: number
  venueDepartmentCode: string | null
}

export const IndividualOffersCard = ({
  venueId,
  venueDepartmentCode,
}: IndividualOffersCardProps): JSX.Element => {
  const { isLoading, data: offers } = useSWR(
    [GET_OFFERS_HOME_QUERY_KEY, venueId],
    () => api.listOffersHome(venueId),
    { fallbackData: [] }
  )

  if (isLoading) {
    return <Skeleton height="15rem" width="100%" />
  }

  if (offers.length === 0) {
    return <OffersRetentionCard variant="INDIVIDUAL" />
  }

  return (
    <Card>
      <Card.Header title={'Activités sur vos offres individuelles'} />
      <Card.Content className={styles['offer-list']}>
        {offers.map((offer) => (
          <IndividualOffersLine
            key={offer.id}
            offer={offer}
            venueDepartmentCode={venueDepartmentCode}
          />
        ))}
      </Card.Content>
      <Card.Footer>
        <Button
          as="a"
          to="/offres"
          label="Voir toutes les offres"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
        />
      </Card.Footer>
    </Card>
  )
}
