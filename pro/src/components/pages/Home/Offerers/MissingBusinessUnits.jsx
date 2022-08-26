import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as PenIcon } from 'icons/ico-outer-pen.svg'
import { Banner } from 'ui-kit'
import { DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

const MissingBusinessUnits = ({ hasTitle }) => {
  return (
    <>
      {hasTitle && (
        <h3 className="h-card-secondary-title">
          Coordonnées bancaires
          <Icon
            alt="Coordonnées bancaires manquantes"
            className="ico-bank-warning"
            svg="ico-alert-filled"
          />
        </h3>
      )}

      <div className="h-card-content">
        <Banner
          links={[
            {
              href: DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL,
              icon: PenIcon,
              linkTitle: 'Renseigner des coordonnées bancaires',
            },
          ]}
        >
          Certains de vos lieux ne sont pas rattachés à des coordonnées
          bancaires. Pour percevoir les remboursements liés aux offres de ces
          lieux, veuillez renseigner des coordonnées bancaires.
        </Banner>
      </div>
    </>
  )
}

MissingBusinessUnits.defaultProps = {
  hasTitle: true,
}

MissingBusinessUnits.propTypes = {
  hasTitle: PropTypes.bool,
}

export default MissingBusinessUnits
