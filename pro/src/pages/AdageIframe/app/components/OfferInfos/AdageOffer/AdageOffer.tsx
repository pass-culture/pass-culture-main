import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
} from 'apiClient/adage'
import strokeArticleIcon from 'icons/stroke-article.svg'
import strokeInfoIcon from 'icons/stroke-info.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageOffer.module.scss'
import AdageOfferDetailsSection from './AdageOfferDetailsSection/AdageOfferDetailsSection'
import AdageOfferInfoSection from './AdageOfferDetailsSection/AdageOfferInfoSection'
import AdageOfferPublicSection from './AdageOfferDetailsSection/AdageOfferPublicSection'
import AdageOfferHeader from './AdageOfferHeader/AdageOfferHeader'

type AdageOfferProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

export default function AdageOffer({ offer }: AdageOfferProps) {
  return (
    <div className={styles['offer']}>
      <div className={styles['offer-header']}>
        <AdageOfferHeader offer={offer} />
      </div>
      <div className={styles['offer-body']}>
        <div className={styles['offer-main']}>
          <div className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeArticleIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Détails de l’offre
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferDetailsSection offer={offer} />
            </div>
          </div>

          <div className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeInfoIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Informations pratiques
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferInfoSection offer={offer} />
            </div>
          </div>
          <div className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeUserIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Public concerné
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferPublicSection offer={offer} />
            </div>
          </div>
        </div>
      </div>
      <div className={styles['offer-side']}>
        {/* TODO : Here will go the side panel */}
      </div>
    </div>
  )
}
