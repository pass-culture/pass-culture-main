import React from 'react'

import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'

const OfferRefundWarning = () => {
  return (
    <Banner
      links={[
        {
          href: CGU_URL,
          linkTitle: "Consulter les Conditions Générales d'Utilisation",
        },
      ]}
      type="attention"
    >
      Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus
      d’informations sur les catégories éligibles au remboursement, merci de
      consulter les CGU.
    </Banner>
  )
}

export default OfferRefundWarning
