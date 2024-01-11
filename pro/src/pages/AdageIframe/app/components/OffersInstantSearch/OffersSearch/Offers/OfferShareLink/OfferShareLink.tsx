import strokeShareIcon from 'icons/stroke-share.svg'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import ListIconButton from 'ui-kit/ListIconButton'

import styles from './OfferShareLink.module.scss'

export interface OfferShareLinkProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  className?: string
}

const OfferShareLink = ({ offer }: OfferShareLinkProps): JSX.Element => {
  const mailBody = `
Bonjour,
%0D%0A%0D%0AJe partage avec vous cette offre pass Culture “${offer.name}”. 
%0D%0A%0D%0APour accéder au descriptif complet de cette offre, veuillez d’abord vous connecter à Adage avec le profil “Rédacteur de projets” ou “Chef d’établissement”, puis cliquez sur le lien : ${document.referrer}adage/passculture/offres/offerid/${offer.id} 
%0D%0A%0D%0AVous ne pouvez pas accéder à ADAGE ? Contactez votre chef d'établissement pour obtenir les droits, cette vidéo pourra l'aider à réaliser la procédure : https://www.dailymotion.com/video/x7ypdmf
%0D%0A%0D%0ACordialement
  `

  return (
    <ListIconButton
      className={styles['share-link']}
      url={`mailto:?subject=Partage d’offre sur ADAGE - ${offer.name}&body=${mailBody}`}
      isExternal={true}
      icon={strokeShareIcon}
    >
      Partager l’offre par email
    </ListIconButton>
  )
}

export default OfferShareLink
