import type { CollectiveOfferResponseModel } from '@/apiClient/adage'

import styles from '../AdageOffer.module.scss'

export type AdageOfferPartnerSectionProps = {
  offer: CollectiveOfferResponseModel
}

export function AdageOfferPartnerSection({
  offer,
}: Readonly<AdageOfferPartnerSectionProps>) {
  return (
    <>
      {offer.contactPhone && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Téléphone
          </h3>
          <p className={styles['offer-section-group-item-text']}>
            {offer.contactPhone}
          </p>
        </div>
      )}

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>E-mail</h3>
        <p className={styles['offer-section-group-item-text']}>
          {offer.contactEmail}
        </p>
      </div>
    </>
  )
}
