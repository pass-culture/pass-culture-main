import React from 'react'

import Banner from 'ui-kit/Banner'

interface Props {
  closable?: boolean
  onClose?: () => void
}

const BannerRGS = ({ closable = false, onClose }: Props): JSX.Element => (
  <Banner
    closable={closable}
    handleOnClick={() => onClose?.()}
    href="https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-"
    linkTitle="Consulter nos recommandations de sécurité"
    type="attention"
  >
    <strong>Soyez vigilant !</strong>
    <br />
    Vos identifiants de connexion sont personnels et ne doivent pas être
    partagés. Pour assurer la protection de votre compte, découvrez nos
    recommandations.
  </Banner>
)

export default BannerRGS
