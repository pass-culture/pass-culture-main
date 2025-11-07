import { useMemo } from 'react'

import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { ShareLink } from '@/ui-kit/ShareLink/ShareLink'

type ShareTemplateOfferLinkProps = {
  offerId: string
  notifySuccessMessage?: string
  maxLength?: number
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
        label="Lien de partage ADAGE"
        notifySuccessMessage={notifySuccessMessage}
      />
      <div>
        <Callout variant={CalloutVariant.INFO}>
          Veillez à préciser aux enseignants de se connecter à ADAGE avant
          d’ouvrir ce lien de partage sans quoi ils n’y auront pas accès.
        </Callout>
      </div>
    </div>
  )
}
