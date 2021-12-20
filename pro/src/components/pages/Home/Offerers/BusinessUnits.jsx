/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'

const BusinessUnits = ({ offererId, hasTitle = true }) => {
  const businessUnitRoutePath = `/structures/${offererId}/point-de-remboursement/`
  return (
    <>
      {hasTitle && (
        <h3 className="h-card-secondary-title">
          Points de remboursement
          <Icon
            alt="Siret manquant"
            className="ico-bank-warning"
            svg="ico-alert-filled"
          />
        </h3>
      )}

      <div className="h-card-content">
        <Banner
          href={businessUnitRoutePath}
          icon="ico-outer-pen"
          linkTitle="Renseigner un SIRET de référence"
          targetLink="_self"
        >
          Certains de vos points de remboursement ne sont pas rattachés à un
          SIRET. Pour continuer à percevoir vos remboursements, veuillez
          renseigner un SIRET de référence.
        </Banner>
      </div>
    </>
  )
}

BusinessUnits.propTypes = {
  hasTitle: PropTypes.bool.isRequired,
  offererId: PropTypes.string.isRequired,
}

export default BusinessUnits
