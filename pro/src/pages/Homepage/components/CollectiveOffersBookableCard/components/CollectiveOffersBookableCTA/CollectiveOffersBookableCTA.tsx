import { differenceInCalendarDays } from 'date-fns'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import type { CollectiveOffersVariantMap } from '../../../types'

type CollectiveOffersBookableCTAProps = {
  stock: CollectiveOffersVariantMap['BOOKABLE']['collectiveStock']
  offerId: number
  offerLink: string
}

export const CollectiveOffersBookableCTA = ({
  stock,
  offerId,
  offerLink,
}: CollectiveOffersBookableCTAProps): JSX.Element => {
  if (stock) {
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
