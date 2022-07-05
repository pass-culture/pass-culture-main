import Banner from 'ui-kit/Banner'
import React from 'react'

const BannerSummary = (): JSX.Element => (
  <Banner type="notification-info">
    <strong>Vous y êtes presque !</strong>
    <br />
    Vérifiez les informations ci-dessous avant de publier votre offre.
  </Banner>
)

export default BannerSummary
