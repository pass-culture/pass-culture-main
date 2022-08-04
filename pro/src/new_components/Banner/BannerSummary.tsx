import React from 'react'

import Banner from 'ui-kit/Banners/Banner'

const BannerSummary = (): JSX.Element => (
  <Banner type="notification-info">
    <strong>Vous y êtes presque !</strong>
    <br />
    Vérifiez les informations ci-dessous avant de publier votre offre.
  </Banner>
)

export default BannerSummary
