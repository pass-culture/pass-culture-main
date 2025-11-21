import {
  CollectiveOfferDisplayedStatus,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { Banner } from '@/design-system/Banner/Banner'

import styles from './PreviewHeader.module.scss'

type PreviewHeaderProps = {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

const statusLabel: Partial<Record<CollectiveOfferDisplayedStatus, string>> = {
  [CollectiveOfferDisplayedStatus.UNDER_REVIEW]: "en cours d'instruction",
  [CollectiveOfferDisplayedStatus.REJECTED]: 'non conforme',
  [CollectiveOfferDisplayedStatus.CANCELLED]: 'annulée',
  [CollectiveOfferDisplayedStatus.EXPIRED]: 'expirée',
  [CollectiveOfferDisplayedStatus.ENDED]: 'terminée',
  [CollectiveOfferDisplayedStatus.REIMBURSED]: 'terminée',
  [CollectiveOfferDisplayedStatus.ARCHIVED]: 'archivée',
  [CollectiveOfferDisplayedStatus.HIDDEN]: 'en pause',
}

export const PreviewHeader = ({ offer }: PreviewHeaderProps) => {
  const shouldShowCallout = Object.keys(statusLabel).includes(
    offer.displayedStatus
  )

  return (
    <>
      <p>
        Voici un aperçu de votre offre à destination de l’établissement scolaire
        sur la plateforme ADAGE.
      </p>
      {shouldShowCallout && (
        <div className={styles['callout']}>
          <Banner
            description={`Cet aperçu n'est pas visible par l'enseignant car votre offre est ${statusLabel[offer.displayedStatus]}.`}
            title=""
          />
        </div>
      )}
    </>
  )
}
