import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { CGU_URL } from 'utils/config'

const OfferRefundWarning = () => {
  return (
    <Banner
      href={CGU_URL}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      subtitle={
        "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
      }
      type="attention"
    />
  )
}

export default OfferRefundWarning
