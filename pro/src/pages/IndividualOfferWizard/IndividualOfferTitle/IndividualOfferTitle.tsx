import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'

import styles from './IndividualOfferTitle.module.scss'

type IndividualOfferTitleProps = {
  mode: OFFER_WIZARD_MODE
  offer?: GetIndividualOfferResponseModel | null
}

export const IndividualOfferTitle = ({
  mode,
  offer,
}: IndividualOfferTitleProps) => {
  if (
    mode === OFFER_WIZARD_MODE.EDITION ||
    mode === OFFER_WIZARD_MODE.READ_ONLY
  ) {
    const synchronizationTag = offer?.lastProvider?.name ? (
      <Tag
        label={`Synchronisée : ${offer.lastProvider.name}`}
        variant={TagVariant.DEFAULT}
      />
    ) : null

    return (
      <div className={styles['offer-name-title']}>
        {offer?.name}
        {synchronizationTag}
      </div>
    )
  }

  return 'Créer une offre'
}
