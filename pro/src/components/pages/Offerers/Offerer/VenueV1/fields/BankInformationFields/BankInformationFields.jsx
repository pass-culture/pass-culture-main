import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import Icon from 'components/layout/Icon'
import { Banner } from 'ui-kit'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

import ApplicationBanner from '../ApplicationBanner'

import { BicIbanFields } from './BicIbanFields'

const BankInformation = ({ venue, offerer }) => {
  const venueHasBankInformation = !!(venue.iban && venue.bic)
  const offererHasBankInformation = !!(offerer.iban && offerer.bic)
  const venueHasApplicationId = !!venue.demarchesSimplifieesApplicationId

  return (
    <div className="section vp-content-section bank-information">
      <div className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">Coordonnées bancaires du lieu</h2>

        {(venueHasBankInformation || offererHasBankInformation) && (
          <a
            className="tertiary-link"
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon alt="lien externe, nouvel onglet" svg="ico-external-site" />
            Modifier
          </a>
        )}
      </div>

      {venueHasBankInformation ? (
        <BicIbanFields bic={venue.bic} iban={venue.iban} />
      ) : (
        <div>
          {offererHasBankInformation && (
            <BicIbanFields bic={offerer.bic} iban={offerer.iban} />
          )}
          {venueHasApplicationId && (
            <ApplicationBanner
              applicationId={venue.demarchesSimplifieesApplicationId}
            />
          )}
          {!offererHasBankInformation && !venueHasApplicationId && (
            <Fragment>
              <p className="bi-subtitle">
                Aucune coordonnée bancaire renseignée
              </p>
              <Banner
                links={[
                  {
                    href: DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL,
                    linkTitle: 'Renseignez les coordonnées bancaires du lieu',
                  },
                ]}
              >
                Renseignez vos coordonnées bancaires pour ce lieu pour être
                remboursé de vos offres éligibles
              </Banner>
            </Fragment>
          )}
          <Banner
            links={[
              {
                href: 'https://passculture.zendesk.com/hc/fr/articles/4411992051601',
                linkTitle: 'En savoir plus sur les remboursements',
              },
            ]}
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
