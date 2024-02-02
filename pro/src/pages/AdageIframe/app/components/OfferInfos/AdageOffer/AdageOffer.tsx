import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { CollectiveOfferResponseModel } from 'apiClient/v1'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageOffer.module.scss'

type AdageOfferProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

export default function AdageOffer({ offer }: AdageOfferProps) {
  return (
    <div className={styles['offer']}>
      <div className={styles['offer-header']}>
        <div className={styles['offer-header-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={styles['offer-header-image']}
              loading="lazy"
              src={offer.imageUrl}
            />
          ) : (
            <div className={styles['offer-header-image-fallback']}>
              <SvgIcon src={strokeOfferIcon} alt="" width="80" />
            </div>
          )}
        </div>
        <div className={styles['offer-header-details']}>
          <h1 className={styles['offer-header-details-title']}>{offer.name}</h1>
          <div className={styles['offer-header-details-structure']}></div>
          <div className={styles['offer-header-details-infos']}></div>
        </div>
      </div>
      <div className={styles['offer-body']}></div>
    </div>
  )
}
