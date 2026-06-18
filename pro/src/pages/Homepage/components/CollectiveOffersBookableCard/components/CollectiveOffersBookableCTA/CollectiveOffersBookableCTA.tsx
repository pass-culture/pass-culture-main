import { differenceInCalendarDays } from 'date-fns'

import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1'
import { canExpire } from '@/commons/core/OfferEducational/utils/canExpire'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

type CollectiveOffersBookableCTAProps = {
  stock: CollectiveOfferHomeResponseModel['collectiveStock']
  displayedStatus: CollectiveOfferHomeResponseModel['displayedStatus']
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
