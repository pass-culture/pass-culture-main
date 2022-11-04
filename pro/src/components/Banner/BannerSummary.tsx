import React from 'react'

import useActiveFeature from 'hooks/useActiveFeature'
import Banner from 'ui-kit/Banners/Banner'

const BannerSummary = (): JSX.Element => {
  const isDraftOfferActivated = useActiveFeature('OFFER_DRAFT_ENABLED')

  return (
    <>
      {isDraftOfferActivated ? (
        <Banner type="notification-info">
          <strong>Vous y êtes presque !</strong>
          <br />
          Vérifiez les informations ci-dessous avant de publier votre offre.
          <br />
          Si vous souhaitez la publier plus tard, vous pouvez retrouver votre
          brouillon dans la liste de vos offres.
        </Banner>
      ) : (
        <Banner type="notification-info">
          <strong>Vous y êtes presque !</strong>
          <br />
          Vérifiez les informations ci-dessous avant de publier votre offre.
        </Banner>
      )}
    </>
  )
}
export default BannerSummary
