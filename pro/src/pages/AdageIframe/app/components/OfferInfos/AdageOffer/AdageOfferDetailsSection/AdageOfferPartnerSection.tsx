import { CollectiveOfferResponseModel } from 'apiClient/adage'

import styles from '../AdageOffer.module.scss'

export type AdageOfferPartnerSectionProps = {
  offer: CollectiveOfferResponseModel
}

export function AdageOfferPartnerSection({
  offer,
}: AdageOfferPartnerSectionProps) {
  return (
    <>
      {offer.contactPhone && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Téléphone
          </h3>
          {offer.contactPhone}
        </div>
      )}

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>E-mail</h3>
        {offer.contactEmail}
      </div>
    </>
  )
}
