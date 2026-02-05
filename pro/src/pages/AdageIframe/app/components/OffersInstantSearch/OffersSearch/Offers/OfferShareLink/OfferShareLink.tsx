import type { MouseEvent } from 'react'

import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { LOGS_DATA } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import strokeShareIcon from '@/icons/stroke-share.svg'

export interface OfferShareLinkProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}

export const OfferShareLink = ({ offer }: OfferShareLinkProps): JSX.Element => {
  const mailBody = `
Bonjour, \n\nJe partage avec vous l’offre pass Culture “${offer.name}”. \n\nPour accéder au descriptif complet de cette offre, veuillez d’abord vous connecter à ADAGE avec le profil “Rédacteur de projets” ou “Chef d’établissement”, puis cliquez sur le lien : ${document.referrer}adage/passculture/offres/offerid/${offer.id}/source/teacherShareLink \n\nVous n'avez pas de profil rédacteur de projets dans ADAGE ? Contactez votre chef d'établissement pour obtenir les droits, cette vidéo pourra l'aider à réaliser la procédure : https://www.dailymotion.com/video/x7ypdmf \n\nCordialement`

  function handleShareButtonClicked(event: MouseEvent) {
    if (LOGS_DATA) {
      apiAdage.logTrackingCtaShare({
        iframeFrom: location.pathname,
        offerId: offer.id,
        source: '',
      })
    }
    event.stopPropagation()
  }

  return (
    <Button
      as="a"
      variant={ButtonVariant.SECONDARY}
      color={ButtonColor.BRAND}
      to={`mailto:?subject=Partage d’offre sur ADAGE - ${encodeURIComponent(offer.name)}&body=${encodeURIComponent(mailBody)}`}
      icon={strokeShareIcon}
      onClick={handleShareButtonClicked}
      isExternal
      tooltip={'Partager par email'}
    />
  )
}
