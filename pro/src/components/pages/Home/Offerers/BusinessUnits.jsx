/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'

const BankInformations = ({ offererId }) => {
  const businessUnitRoutePath = `/structures/${offererId}/points-de-facturations/`
  return (
    <>
      <h3 className="h-card-secondary-title">
        Points de facturation
        <Icon
          alt="Informations bancaires manquantes"
          className="ico-bank-warning"
          svg="ico-alert-filled"
        />
      </h3>

      <div className="h-card-content">
        <Banner
        href={businessUnitRoutePath}
        linkTitle="Consultez vos points de facturations"
        >
        Certains de vos points de facturation ne sont pas rattachés à SIRET.
        Pour percevoir vos remboursements, veuillez renseignez un SIRET.
        </Banner>
      </div>
    </>
  )
}

BankInformations.propTypes = {
  offererId: PropTypes.string.isRequired,
}

export default BankInformations
