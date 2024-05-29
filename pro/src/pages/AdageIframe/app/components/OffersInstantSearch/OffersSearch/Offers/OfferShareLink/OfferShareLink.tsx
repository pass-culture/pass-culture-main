import { MouseEvent } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import strokeShareIcon from 'icons/stroke-share.svg'
import {
  ListIconButton,
  ListIconButtonVariant,
} from 'ui-kit/ListIconButton/ListIconButton'
import { LOGS_DATA } from 'utils/config'

export interface OfferShareLinkProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  className?: string
  tooltipContentClassName?: string
}

export const OfferShareLink = ({
  offer,
  className,
  tooltipContentClassName,
}: OfferShareLinkProps): JSX.Element => {
  const mailBody = `
Bonjour, \n\nJe partage avec vous l’offre pass Culture “${offer.name}”. \n\nPour accéder au descriptif complet de cette offre, veuillez d’abord vous connecter à ADAGE avec le profil “Rédacteur de projets” ou “Chef d’établissement”, puis cliquez sur le lien : ${document.referrer}adage/passculture/offres/offerid/${offer.id} \n\nVous n'avez pas de profil rédacteur de projets dans ADAGE ? Contactez votre chef d'établissement pour obtenir les droits, cette vidéo pourra l'aider à réaliser la procédure : https://www.dailymotion.com/video/x7ypdmf \n\nCordialement`

  function handleShareButtonClicked(event: MouseEvent) {
    if (LOGS_DATA) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logTrackingCtaShare({
        iframeFrom: location.pathname,
        offerId: offer.id,
        source: '',
      })
    }
    event.stopPropagation()
  }

  return (
    <ListIconButton
      className={className}
      url={`mailto:?subject=Partage d’offre sur ADAGE - ${encodeURIComponent(offer.name)}&body=${encodeURIComponent(mailBody)}`}
      icon={strokeShareIcon}
      onClick={handleShareButtonClicked}
      tooltipContentClassName={tooltipContentClassName}
      variant={ListIconButtonVariant.PRIMARY}
    >
      Partager l’offre par email
    </ListIconButton>
  )
}
