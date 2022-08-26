import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Field } from 'react-final-form'

import Icon from 'components/layout/Icon'
import Spinner from 'components/layout/Spinner'
import { humanizeSiret } from 'core/Venue/utils'
import { getBusinessUnits } from 'repository/pcapi/pcapi'
import { Banner } from 'ui-kit'
import { DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

import ApplicationBanner from '../ApplicationBanner'

const CREATE_DMS_FILE_BANNER = 'create_dms_file_banner'
const REPLACE_DMS_FILE_BUTTON = 'replace_dms_file_button'
const PENDING_DMS_FILE_BANNER = 'pending_dms_file_banner'

const BankInformationWithBusinessUnit = ({
  readOnly,
  offerer,
  scrollToSection,
  venue,
  isCreatingVenue,
}) => {
  const [businessUnitOptions, setBusinessUnitOptions] = useState([])
  const [venueBusinessUnit, setVenueBusinessUnit] = useState(null)
  const [displayedBanners, setDisplayedBanners] = useState({
    [CREATE_DMS_FILE_BANNER]: false,
    [REPLACE_DMS_FILE_BUTTON]: false,
    [PENDING_DMS_FILE_BANNER]: false,
  })
  const [isLoading, setIsLoading] = useState(true)

  const businessUnitDisplayName = businessUnit =>
    businessUnit
      ? `${
          businessUnit.siret
            ? humanizeSiret(businessUnit.siret)
            : 'SIRET manquant'
        } - ${businessUnit.iban}`
      : ''

  const scrollToBusinessUnit = useCallback(node => {
    if (scrollToSection && node) {
      node.scrollIntoView()
    }
  }, [])

  useEffect(() => {
    async function loadBusinessUnits(offererId) {
      const businessUnitsResponse = await getBusinessUnits(offererId)

      let venueBusinessUnitResponse = null
      if (venue.businessUnit) {
        if (venue.businessUnit.siret) {
          venueBusinessUnitResponse = businessUnitsResponse.find(
            businessUnit => businessUnit.id === venue.businessUnitId
          )
        } else {
          venueBusinessUnitResponse = {
            iban: venue.businessUnit.iban,
            siret: '',
            id: venue.businessUnit.id,
          }
        }
      }
      setVenueBusinessUnit(venueBusinessUnitResponse)
      setBusinessUnitOptions(
        businessUnitsResponse
          .filter(
            businessUnit =>
              businessUnit.siret !== null ||
              businessUnit.id === venue.businessUnitId
          )
          .map(businessUnit => ({
            key: `venue-business-unit-${businessUnit.id}`,
            displayName: businessUnitDisplayName(businessUnit),
            id: businessUnit.id,
          }))
      )

      setDisplayedBanners({
        [CREATE_DMS_FILE_BANNER]: isCreatingVenue
          ? true
          : venue.id && !venue.isBusinessUnitMainVenue && !venue.isVirtual,
        [REPLACE_DMS_FILE_BUTTON]: venue.id && venue.isBusinessUnitMainVenue,
        [PENDING_DMS_FILE_BANNER]:
          venue.id &&
          !venue.iban &&
          !venue.bic &&
          venue.demarchesSimplifieesApplicationId &&
          !venue.isVirtual,
      })
      setIsLoading(false)
    }
    loadBusinessUnits(offerer.id)
  }, [
    isCreatingVenue,
    offerer.id,
    setDisplayedBanners,
    venue.bic,
    venue.businessUnit,
    venue.businessUnitId,
    venue.demarchesSimplifieesApplicationId,
    venue.iban,
    venue.id,
    venue.isBusinessUnitMainVenue,
    venue.isVirtual,
    venue.siret,
  ])

  if (isLoading) return <Spinner />
  if (!venue.isVirtual || !!businessUnitOptions.length)
    return (
      <div className="section vp-content-section bank-information">
        <div className="main-list-title title-actions-container">
          <h2 ref={scrollToBusinessUnit} className="main-list-title-text">
            Coordonnées bancaires du lieu
          </h2>
          {displayedBanners[REPLACE_DMS_FILE_BUTTON] && (
            <a
              className="tertiary-link"
              href={
                DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL
              }
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon alt="lien externe, nouvel onglet" svg="ico-external-site" />
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
                    <option disabled value="">
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
              links={[
                {
                  href: DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL,
                  linkTitle: 'Ajouter des coordonnées bancaires',
                },
              ]}
            >
              Pour ajouter de nouvelles coordonnées bancaires, rendez-vous sur
              Démarches Simplifiées.
            </Banner>
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
      </div>
    )
  return null
}

BankInformationWithBusinessUnit.defaultProps = {
  isCreatingVenue: false,
  readOnly: false,
  scrollToSection: false,
  venue: {},
}
BankInformationWithBusinessUnit.propTypes = {
  isCreatingVenue: PropTypes.bool,
  offerer: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
  scrollToSection: PropTypes.bool,
  venue: PropTypes.shape(),
}

export default BankInformationWithBusinessUnit
