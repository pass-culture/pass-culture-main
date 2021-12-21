/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { Field } from 'react-final-form'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'
import Spinner from 'components/layout/Spinner'
import { getBusinessUnits } from 'repository/pcapi/pcapi'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

import { formatSiret } from '../../siret/formatSiret'

import { ApplicationBanner } from './ApplicationBanner'

const CREATE_DMS_FILE_BANNER = 'create_dms_file_banner'
const REPLACE_DMS_FILE_BUTTON = 'replace_dms_file_button'
const PENDING_DMS_FILE_BANNER = 'pending_dms_file_banner'

const BankInformationWithBusinessUnit = ({ readOnly, offerer, venue }) => {
  const [businessUnitOptions, setBusinessUnitOptions] = useState([])
  const [venueBusinessUnit, setVenueBusinessUnit] = useState(null)
  const [displayedBanners, setDisplayedBanners] = useState({
    [CREATE_DMS_FILE_BANNER]: false,
    [REPLACE_DMS_FILE_BUTTON]: false,
    [PENDING_DMS_FILE_BANNER]: false,
  })
  const [isLoading, setIsLoading] = useState(true)

  const businessUnitDisplayName = businessUnit =>
    `${formatSiret(businessUnit.siret)} - ${businessUnit.iban}`

  useEffect(() => {
    async function loadBusinessUnits(offererId) {
      const businessUnitsResponse = await getBusinessUnits(offererId)
      const venueBusinessUnitResponse = businessUnitsResponse.find(
        businessUnit => businessUnit.id === venue.businessUnitId
      )

      setVenueBusinessUnit(venueBusinessUnitResponse)
      setBusinessUnitOptions(
        businessUnitsResponse
          .filter(businessUnit => businessUnit.siret != null)
          .map(businessUnit => ({
            key: `venue-business-unit-${businessUnit.id}`,
            displayName: businessUnitDisplayName(businessUnit),
            id: businessUnit.id,
          }))
      )

      setDisplayedBanners({
        [CREATE_DMS_FILE_BANNER]: venue.id && !venue.isBusinessUnitMainVenue,
        [REPLACE_DMS_FILE_BUTTON]: venue.id && venue.isBusinessUnitMainVenue,
        [PENDING_DMS_FILE_BANNER]:
          venue.id &&
          !venue.businessUnitId &&
          venue.demarchesSimplifieesApplicationId,
      })
      setIsLoading(false)
    }
    loadBusinessUnits(offerer.id)
  }, [
    offerer.id,
    setDisplayedBanners,
    venue.id,
    venue.businessUnitId,
    venue.demarchesSimplifieesApplicationId,
    venue.isBusinessUnitMainVenue,
    venue.siret,
  ])

  if (isLoading) return <Spinner />
  return (
    <div className="section vp-content-section bank-information">
      <div className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">
          Coordonnées bancaires du lieu (remboursement)
        </h2>
        {displayedBanners[REPLACE_DMS_FILE_BUTTON] && (
          <a
            className="tertiary-link"
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon alt="" svg="ico-external-site" />
            Modifier
          </a>
        )}
      </div>
      <p className="bi-subtitle">
        Ces coordonnées bancaires seront utilisées pour les remboursements des
        offres éligibles de ce lieu.
      </p>
      {!!businessUnitOptions.length && (
        <div className="field field-select">
          <div className="field-label">
            <label htmlFor="venue-business-unit">
              Coordonnées bancaires pour vos remboursements :
            </label>
          </div>
          {readOnly ? (
            businessUnitDisplayName(venueBusinessUnit)
          ) : (
            <div className="control control-select">
              <div className="select">
                <Field
                  component="select"
                  id="venue-business-unit"
                  name="businessUnitId"
                  readOnly={readOnly}
                >
                  <option value="">
                    Sélectionner des coordonnées dans la liste
                  </option>
                  {businessUnitOptions.map(option => (
                    <option key={option.key} value={option.id}>
                      {option.displayName}
                    </option>
                  ))}
                </Field>
              </div>
            </div>
          )}
        </div>
      )}
      <div className="banners">
        {displayedBanners[PENDING_DMS_FILE_BANNER] && (
          <ApplicationBanner
            applicationId={venue.demarchesSimplifieesApplicationId}
          />
        )}
        {displayedBanners[CREATE_DMS_FILE_BANNER] && (
          <Banner
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            linkTitle="Rendez-vous sur Démarches Simplifiées"
          >
            Vous souhaitez modifier ou ajouter des coordonnées bancaires ?
          </Banner>
        )}
        <Banner
          href="https://aide.passculture.app/fr/articles/5096833-calendrier-des-prochains-remboursements"
          linkTitle="En savoir plus sur les remboursements"
          type="notification-info"
        />
      </div>
    </div>
  )
}

BankInformationWithBusinessUnit.defaultProps = {
  readOnly: false,
  venue: {},
}
BankInformationWithBusinessUnit.propTypes = {
  offerer: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
  venue: PropTypes.shape(),
}

export default BankInformationWithBusinessUnit
