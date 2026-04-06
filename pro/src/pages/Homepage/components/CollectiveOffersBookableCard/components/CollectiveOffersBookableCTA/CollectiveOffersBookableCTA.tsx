import { differenceInCalendarDays } from 'date-fns'

import { canExpire } from '@/commons/core/OfferEducational/utils/canExpire'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import type { CollectiveOffersVariantMap } from '@/pages/Homepage/components/types'

type CollectiveOffersBookableCTAProps = {
  stock: CollectiveOffersVariantMap['BOOKABLE']['collectiveStock']
  displayedStatus: CollectiveOffersVariantMap['BOOKABLE']['displayedStatus']
  offerId: number
  offerLink: string
}

export const CollectiveOffersBookableCTA = ({
  stock,
  displayedStatus,
  offerId,
  offerLink,
}: CollectiveOffersBookableCTAProps): JSX.Element => {
  if (stock && canExpire({ displayedStatus })) {
    const daysCountBeforeExpiration = differenceInCalendarDays(
      new Date(stock.bookingLimitDatetime),
      new Date()
    )

    if (daysCountBeforeExpiration <= 7) {
      const stockEditionLink = `/offre/${offerId}/collectif/stocks/edition`
      return (
        <Button
          variant={ButtonVariant.SECONDARY}
          label="Modifier la date limite"
          as="a"
          to={stockEditionLink}
        />
      )
    }
  }
  return (
    <Button
      variant={ButtonVariant.SECONDARY}
      label="Voir l'offre"
      as="a"
      to={offerLink}
    />
  )
}
