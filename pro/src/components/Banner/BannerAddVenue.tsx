import React from 'react'

import InternalBanner from 'ui-kit/Banners/InternalBanner'

interface BannerAddVenueProps {
  offererId: string
}

const BannerAddVenue = ({ offererId }: BannerAddVenueProps): JSX.Element => (
  <InternalBanner
    to={`/structures/${offererId}/lieux/creation`}
    linkTitle="+ Ajouter un lieu"
    subtitle="Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures."
    type="notification-info"
  />
)

export default BannerAddVenue
