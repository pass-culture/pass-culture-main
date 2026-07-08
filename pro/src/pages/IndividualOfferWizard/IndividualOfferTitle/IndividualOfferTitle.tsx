import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'

import styles from './IndividualOfferTitle.module.scss'

type IndividualOfferTitleProps = {
  mode: OFFER_WIZARD_MODE
  offer?: GetIndividualOfferWithAddressResponseModel | null
}

export const IndividualOfferTitle = ({
  mode,
  offer,
}: IndividualOfferTitleProps) => {
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  if (!isOfferExposureEnabled && mode === OFFER_WIZARD_MODE.EDITION) {
    return 'Modifier l’offre'
  }

  if (
    mode === OFFER_WIZARD_MODE.EDITION ||
    mode === OFFER_WIZARD_MODE.READ_ONLY
  ) {
    const synchronizationTag =
      isOfferExposureEnabled && offer?.lastProvider?.name ? (
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
