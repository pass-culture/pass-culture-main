import React from 'react'

import Callout from 'components/Callout/Callout'
import fullLinkIcon from 'icons/full-link.svg'

interface Props {
  closable?: boolean
  onClose?: () => void
}

const BannerRGS: React.FC<Props> = ({ closable, onClose }: Props) => (
  <Callout
    closable={closable}
    onClose={onClose}
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-',
        linkTitle: 'Consulter nos recommandations de sécurité',
        icon: fullLinkIcon,
        svgAlt: 'Nouvelle fenêtre',
      },
    ]}
  >
    <strong>Soyez vigilant !</strong>
    <br />
    Vos identifiants de connexion sont personnels et ne doivent pas être
    partagés. Pour assurer la protection de votre compte, découvrez nos
    recommandations.
  </Callout>
)

export default BannerRGS
