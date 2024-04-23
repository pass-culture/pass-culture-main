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

const OfferShareLink = ({
  offer,
  className,
  tooltipContentClassName,
}: OfferShareLinkProps): JSX.Element => {
  const mailBody = `
Bonjour,
%0D%0A%0D%0AJe partage avec vous l’offre pass Culture “${offer.name}”. 
%0D%0A%0D%0APour accéder au descriptif complet de cette offre, veuillez d’abord vous connecter à Adage avec le profil “Rédacteur de projets” ou “Chef d’établissement”, puis cliquez sur le lien : ${document.referrer}adage/passculture/offres/offerid/${offer.id} 
%0D%0A%0D%0AVous n'avez pas de profil rédacteur de projets dans ADAGE ? Contactez votre chef d'établissement pour obtenir les droits, cette vidéo pourra l'aider à réaliser la procédure : https://www.dailymotion.com/video/x7ypdmf
%0D%0A%0D%0ACordialement
  `

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
      url={`mailto:?subject=Partage d’offre sur ADAGE - ${offer.name}&body=${mailBody}`}
      icon={strokeShareIcon}
      onClick={handleShareButtonClicked}
      tooltipContentClassName={tooltipContentClassName}
      variant={ListIconButtonVariant.PRIMARY}
    >
      Partager l’offre par email
    </ListIconButton>
  )
}

export default OfferShareLink
