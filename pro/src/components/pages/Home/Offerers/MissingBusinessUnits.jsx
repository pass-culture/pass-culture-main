/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import InternalBanner from 'components/layout/InternalBanner'
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
        <InternalBanner
          href={DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL}
          icon="ico-pen-black"
          linkTitle="Renseignez les coordonnées bancaires"
          targetLink="_self"
        >
          Certains de vos lieux ne sont pas rattachés à des coordonnées
          bancaires. Pour percevoir les remboursements liés aux offres postées
          dans ces lieux, renseignez les coordonnées bancaires.
        </InternalBanner>
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
