import classNames from 'classnames'

import { apiAdage } from 'apiClient/api'
import strokeShareIcon from 'icons/stroke-share.svg'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import ListIconButton from 'ui-kit/ListIconButton'
import { LOGS_DATA } from 'utils/config'

import styles from './OfferShareLink.module.scss'

export interface OfferShareLinkProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  className?: string
}

const OfferShareLink = ({
  offer,
  className,
}: OfferShareLinkProps): JSX.Element => {
  const mailBody = `
Bonjour,
%0D%0A%0D%0AJe partage avec vous l’offre pass Culture “${offer.name}”. 
%0D%0A%0D%0APour accéder au descriptif complet de cette offre, veuillez d’abord vous connecter à Adage avec le profil “Rédacteur de projets” ou “Chef d’établissement”, puis cliquez sur le lien : ${document.referrer}adage/passculture/offres/offerid/${offer.id} 
%0D%0A%0D%0AVous n'avez pas de profil rédacteur de projets dans ADAGE ? Contactez votre chef d'établissement pour obtenir les droits, cette vidéo pourra l'aider à réaliser la procédure : https://www.dailymotion.com/video/x7ypdmf
%0D%0A%0D%0ACordialement
  `

  function handleShareButtonClicked() {
    if (LOGS_DATA) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logTrackingCtaShare({
        iframeFrom: location.pathname,
        offerId: offer.id,
        source: '',
      })
    }
  }

  return (
    <ListIconButton
      className={classNames(styles['share-link'], className)}
      url={`mailto:?subject=Partage d’offre sur ADAGE - ${offer.name}&body=${mailBody}`}
      icon={strokeShareIcon}
      onClick={handleShareButtonClicked}
    >
      Partager l’offre par email
    </ListIconButton>
  )
}

export default OfferShareLink
