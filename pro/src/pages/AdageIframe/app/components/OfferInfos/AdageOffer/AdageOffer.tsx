import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
  AuthenticatedResponse,
} from 'apiClient/adage'
import strokeArticleIcon from 'icons/stroke-article.svg'
import strokeInfoIcon from 'icons/stroke-info.svg'
import strokeInstitutionIcon from 'icons/stroke-institution.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { isCollectiveOfferBookable } from 'pages/AdageIframe/app/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AdageOffer.module.scss'
import { AdageOfferDetailsSection } from './AdageOfferDetailsSection/AdageOfferDetailsSection'
import { AdageOfferInfoSection } from './AdageOfferDetailsSection/AdageOfferInfoSection'
import { AdageOfferPartnerSection } from './AdageOfferDetailsSection/AdageOfferPartnerSection'
import { AdageOfferPublicSection } from './AdageOfferDetailsSection/AdageOfferPublicSection'
import { AdageOfferHeader } from './AdageOfferHeader/AdageOfferHeader'
import { AdageOfferInstitutionPanel } from './AdageOfferInstitutionPanel/AdageOfferInstitutionPanel'
import { AdageOfferPartnerPanel } from './AdageOfferPartnerPanel/AdageOfferPartnerPanel'

export type AdageOfferProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  adageUser?: AuthenticatedResponse
  isPreview?: boolean
  setInstitutionOfferCount?: (value: number) => void
  institutionOfferCount?: number
}

export const AdageOffer = ({
  offer,
  adageUser,
  isPreview = false,
  setInstitutionOfferCount,
  institutionOfferCount,
}: AdageOfferProps) => {
  const isOfferBookable = isCollectiveOfferBookable(offer)

  return (
    <div className={styles['offer']}>
      <div className={styles['offer-header']}>
        <AdageOfferHeader
          offer={offer}
          adageUser={adageUser}
          isPreview={isPreview}
        />
      </div>
      <div className={styles['offer-body']}>
        <div className={styles['offer-main']}>
          <section className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeArticleIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Détails de l’offre
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferDetailsSection offer={offer} />
            </div>
          </section>

          <section className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeInfoIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Informations pratiques
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferInfoSection offer={offer} />
            </div>
          </section>
          <section className={styles['offer-section']}>
            <div className={styles['offer-section-header']}>
              <SvgIcon alt="" src={strokeUserIcon} width="24" />
              <h2 className={styles['offer-section-header-title']}>
                Public concerné
              </h2>
            </div>

            <div className={styles['offer-section-group']}>
              <AdageOfferPublicSection offer={offer} />
            </div>
          </section>
          {isOfferBookable && (
            <section className={styles['offer-section']}>
              <div className={styles['offer-section-header']}>
                <SvgIcon alt="" src={strokeInstitutionIcon} width="24" />
                <h2 className={styles['offer-section-header-title']}>
                  Contact du partenaire culturel
                </h2>
              </div>

              <div className={styles['offer-section-group']}>
                <AdageOfferPartnerSection offer={offer} />
              </div>
            </section>
          )}
        </div>
        <div className={styles['offer-side']}>
          {isOfferBookable ? (
            (offer.teacher || offer.educationalInstitution) && (
              <AdageOfferInstitutionPanel
                offer={offer}
                adageUser={adageUser}
                isPreview={isPreview}
                setInstitutionOfferCount={setInstitutionOfferCount}
                institutionOfferCount={institutionOfferCount}
              />
            )
          ) : (
            <AdageOfferPartnerPanel
              offer={offer}
              adageUser={adageUser}
              isPreview={isPreview}
            />
          )}
        </div>
      </div>
    </div>
  )
}
