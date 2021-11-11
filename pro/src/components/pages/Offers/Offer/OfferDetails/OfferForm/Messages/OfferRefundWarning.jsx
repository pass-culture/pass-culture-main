/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { CGU_URL } from 'utils/config'

const OfferRefundWarning = () => {
  return (
    <Banner
      href={CGU_URL}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      type="attention"
    >
      Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les
      catégories éligibles au remboursement, merci de consulter les CGU.
    </Banner>
  )
}

export default OfferRefundWarning
