import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import InternalBanner from 'ui-kit/Banners/InternalBanner'

const InvalidBusinessUnits = ({ offererId, hasTitle = true }) => {
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
        <InternalBanner
          to={businessUnitRoutePath}
          Icon={PenIcon}
          linkTitle="Renseigner un SIRET de référence"
          targetLink="_self"
        >
          Certains de vos points de remboursement ne sont pas rattachés à un
          SIRET. Pour continuer à percevoir vos remboursements, veuillez
          renseigner un SIRET de référence.
        </InternalBanner>
      </div>
    </>
  )
}

InvalidBusinessUnits.propTypes = {
  hasTitle: PropTypes.bool.isRequired,
  offererId: PropTypes.string.isRequired,
}

export default InvalidBusinessUnits
