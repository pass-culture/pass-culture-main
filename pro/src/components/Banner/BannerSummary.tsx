import React from 'react'

import { OFFER_WIZARD_MODE } from 'core/Offers'
import Banner from 'ui-kit/Banners/Banner'

interface BannerSummaryProps {
  mode: OFFER_WIZARD_MODE
}

const BannerSummary = ({ mode }: BannerSummaryProps): JSX.Element => {
  return (
    <>
      <Banner type="notification-info">
        <strong>Vous y êtes presque !</strong>
        <br />
        Vérifiez les informations ci-dessous avant de publier votre offre.
        {mode === OFFER_WIZARD_MODE.CREATION && (
          <>
            <br />
            Si vous souhaitez la publier plus tard, vous pouvez retrouver votre
            brouillon dans la liste de vos offres.
          </>
        )}
      </Banner>
    </>
  )
}
export default BannerSummary
