import React from 'react'

import Icon from 'components/layout/Icon'
import Insert from 'components/layout/Insert/Insert'
import { CGU_URL } from 'utils/config'

const OfferRefundWarning = () => {
  return (
    <Insert className="yellow-insert">
      <p>
        {
          "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
        }
      </p>
      <div className="insert-action-link">
        <a
          href={CGU_URL}
          id="cgu-link"
          rel="noopener noreferrer"
          target="_blank"
        >
          <Icon svg="ico-external-site" />
          <p>
            {"Consulter les Conditions Générales d'Utilisation"}
          </p>
        </a>
      </div>
    </Insert>
  )
}

export default OfferRefundWarning
