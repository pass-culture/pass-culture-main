import { useMemo } from 'react'

import { ADAGE_URL } from '@/commons/utils/config'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { ShareLink } from '@/ui-kit/ShareLink/ShareLink'

import styles from './ShareTemplateOfferLink.module.scss'

export type ShareTemplateOfferLinkProps = {
  offerId: number
  notifySuccessMessage?: string
}

export const ShareTemplateOfferLink = ({
  offerId,
  notifySuccessMessage = 'Le lien ADAGE a bien été copié',
}: ShareTemplateOfferLinkProps) => {
  const fullLink = useMemo(
    () => `${ADAGE_URL}/offerid/${offerId}/source/shareLink`,
    [offerId]
  )

  return (
    <div>
      <ShareLink
        link={fullLink}
        label="Lien de l’offre"
        notifySuccessMessage={notifySuccessMessage}
        offerId={offerId}
      />
      <div className={styles['callout-container']}>
        <Banner
          title="Connexion à ADAGE obligatoire"
          variant={BannerVariants.DEFAULT}
          description="Veillez à préciser aux enseignants de se connecter à ADAGE avant
            d’ouvrir ce lien de partage sans quoi ils n’y auront pas accès."
        />
      </div>
    </div>
  )
}
