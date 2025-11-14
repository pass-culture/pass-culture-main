import { useMemo } from 'react'

import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { ShareLink } from '@/ui-kit/ShareLink/ShareLink'

import styles from './ShareTemplateOfferLink.module.scss'

export type ShareTemplateOfferLinkProps = {
  offerId: number
  notifySuccessMessage?: string
}

const ADAGE_BASE_URL =
  'https://bv.ac-versailles.fr/adage/passculture/offres/offerid/'

export const ShareTemplateOfferLink = ({
  offerId,
  notifySuccessMessage = 'Le lien ADAGE a bien été copié',
}: ShareTemplateOfferLinkProps) => {
  const fullLink = useMemo(
    () => `${ADAGE_BASE_URL}${offerId}?source=shareLink`,
    [offerId]
  )

  return (
    <div>
      <ShareLink
        link={fullLink}
        label="Lien de l’offre"
        notifySuccessMessage={notifySuccessMessage}
      />
      <div className={styles['callout-container']}>
        <Callout
          title="Connexion à ADAGE obligatoire"
          variant={CalloutVariant.INFO}
        >
          <div className={styles['callout-content']}>
            Veillez à préciser aux enseignants de se connecter à ADAGE avant
            d’ouvrir ce lien de partage sans quoi ils n’y auront pas accès.
          </div>
        </Callout>
      </div>
    </div>
  )
}
