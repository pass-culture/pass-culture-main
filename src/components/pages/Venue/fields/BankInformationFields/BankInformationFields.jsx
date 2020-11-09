import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import Banner from 'components/layout/Banner/Banner'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

import { ApplicationBanner } from './ApplicationBanner'
import { BicIbanFields } from './BicIbanFields'

const BankInformation = ({ venue, offerer }) => {
  const venueHasBankInformation = !!(venue.iban && venue.bic)
  const offererHasBankInformation = !!(offerer.iban && offerer.bic)
  const venueHasApplicationId = !!venue.demarchesSimplifieesApplicationId

  return (
    <div className="section vp-content-section bank-information">
      <h2 className="main-list-title">
        {'Coordonnées bancaires du lieu'}
      </h2>

      {venueHasBankInformation ? (
        <BicIbanFields
          bic={venue.bic}
          iban={venue.iban}
        />
      ) : (
        <div>
          {offererHasBankInformation && (
            <BicIbanFields
              bic={offerer.bic}
              iban={offerer.iban}
            />
          )}
          {venueHasApplicationId && (
            <ApplicationBanner applicationId={venue.demarchesSimplifieesApplicationId} />
          )}
          {!offererHasBankInformation && !venueHasApplicationId && (
            <Fragment>
              <p className="bi-subtitle">
                {'Aucune coordonnée bancaire renseignée'}
              </p>
              <Banner
                href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
                linkTitle="Renseignez les coordonnées bancaires du lieu"
                subtitle="Renseignez vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles"
              />
            </Fragment>
          )}
          <Banner
            href="https://aide.passculture.app/fr/article/acteurs-determiner-ses-modalites-de-remboursement-1ab6g2m/"
            linkTitle="En savoir plus sur les remboursements"
            type="notification-info"
          />
        </div>
      )}
    </div>
  )
}

BankInformation.defaultProps = {
  venue: {},
}
BankInformation.propTypes = {
  offerer: PropTypes.shape().isRequired,
  venue: PropTypes.shape(),
}

export default BankInformation
