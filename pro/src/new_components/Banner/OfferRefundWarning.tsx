import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'
import React from 'react'

const OfferRefundWarning = () => {
  return (
    <Banner
      href={CGU_URL}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      type="attention"
    >
      Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus
      d’informations sur les catégories éligibles au remboursement, merci de
      consulter les CGU.
    </Banner>
  )
}

export default OfferRefundWarning
