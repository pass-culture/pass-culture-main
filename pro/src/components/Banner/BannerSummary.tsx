import React from 'react'

import Banner from 'ui-kit/Banners/Banner'

const BannerSummary = (): JSX.Element => {
  return (
    <>
      <Banner type="notification-info">
        <strong>Vous y êtes presque !</strong>
        <br />
        Vérifiez les informations ci-dessous avant de publier votre offre.
        <br />
        Si vous souhaitez la publier plus tard, vous pouvez retrouver votre
        brouillon dans la liste de vos offres.
      </Banner>
    </>
  )
}
export default BannerSummary
