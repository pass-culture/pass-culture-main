import React, { useCallback, useEffect, useState } from 'react'

import ApplicationBanner from '../ApplicationBanner'
import { DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'
import { Field } from 'react-final-form'
import PropTypes from 'prop-types'
import Spinner from 'components/layout/Spinner'
import { Title } from 'ui-kit'

import { getBusinessUnits } from 'repository/pcapi/pcapi'
import { humanizeSiret } from 'core/Venue/utils'

import styles from './ReimbursementPoint.module.scss'

const ReimbursementPoint = ({
  readOnly,
  offerer,
  scrollToSection,
  venue,
  isCreatingVenue,
}) => {
  const [reimbursementPointOptions, setReimbursementPointOptions] = useState([])
  const [venueReimbursementPoint, setVenueReimbursementPoint] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasPendingDmsApplication, setHasPendingDmsApplication] =
    useState(false)

  const businessUnitDisplayName = businessUnit =>
    businessUnit
      ? `${
          businessUnit.siret
            ? humanizeSiret(businessUnit.siret)
            : 'SIRET manquant'
        } - ${businessUnit.iban}`
      : ''

  const modifyReimbursementPointLabel = useCallback(() => {
    return venue.isBusinessUnitMainVenue
      ? 'Modifier mes coordonnées bancaires'
      : 'Ajouter des coordonnées bancaires'
  }, [venue.isBusinessUnitMainVenue, venueReimbursementPoint])

  const scrollToReimbursementPoint = useCallback(reimbursementPoint => {
    if (scrollToSection && reimbursementPoint) {
      reimbursementPoint.scrollIntoView()
    }
  }, [])

  const openDMSApplication = useCallback(() => {
    window.open(
      DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL,
      '_blank'
    )
  })

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
      setVenueReimbursementPoint(venueBusinessUnitResponse)
      setReimbursementPointOptions(
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
      setHasPendingDmsApplication(
        venue.id &&
          !venue.iban &&
          !venue.bic &&
          venue.demarchesSimplifieesApplicationId &&
          !venue.isVirtual
      )
      setIsLoading(false)
    }
    loadBusinessUnits(offerer.id)
  }, [
    isCreatingVenue,
    offerer.id,
    readOnly,
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
  if (!venue.isVirtual)
    return (
      <div className="section reimbursement-point-section">
        <div className="main-list-title" ref={scrollToReimbursementPoint}>
          <Title as="h2" level={4} className={styles['sub-title-text']}>
            Coordonnées bancaires
          </Title>
        </div>
        {hasPendingDmsApplication ? (
          <ApplicationBanner
            applicationId={venue.demarchesSimplifieesApplicationId}
          />
        ) : (
          <>
            <p className={styles['section-description']}>
              Ces coordonnées bancaires seront utilisées pour les remboursements
              des offres éligibles de ce lieu.
            </p>
            {!venueReimbursementPoint && (
              <div className={styles['add-reimbursement-point-section']}>
                <button
                  className="secondary-button"
                  id="add-new-reimbursement-point"
                  onClick={openDMSApplication}
                  type="button"
                >
                  Ajouter des coordonnées bancaires
                </button>
              </div>
            )}
            {!venueReimbursementPoint && !!reimbursementPointOptions.length && (
              <p className={styles['or-separator']}>ou</p>
            )}
            {!!reimbursementPointOptions.length && (
              <div className={styles['field-select']}>
                {!venueReimbursementPoint && (
                  <p className={styles['select-description']}>
                    <b>Sélectionner</b> des coordonnées bancaires parmi celles
                    déjà existantes dans votre structure :
                  </p>
                )}
                <div className={styles['label-reimbursment-point']}>
                  <label htmlFor="venue-reimbursement-point">
                    Coordonnées bancaires
                  </label>
                </div>

                <div className={styles['select']}>
                  <Field
                    component="select"
                    id="venue-reimbursement-point"
                    name="businessUnitId"
                    disabled={readOnly}
                  >
                    <option disabled value="">
                      Sélectionner des coordonnées dans la liste
                    </option>
                    {reimbursementPointOptions.map(option => (
                      <option key={option.key} value={option.id}>
                        {option.displayName}
                      </option>
                    ))}
                  </Field>
                </div>
                {(venueReimbursementPoint || venue.isBusinessUnitMainVenue) && (
                  <div className={styles['modify-reimbursement-point-section']}>
                    <button
                      className="secondary-button"
                      id="modify-new-reimbursement-point"
                      onClick={openDMSApplication}
                      type="button"
                    >
                      {modifyReimbursementPointLabel()}
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    )
  return null
}

ReimbursementPoint.defaultProps = {
  isCreatingVenue: false,
  readOnly: false,
  scrollToSection: false,
  venue: {},
}
ReimbursementPoint.propTypes = {
  isCreatingVenue: PropTypes.bool,
  offerer: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
  scrollToSection: PropTypes.bool,
  venue: PropTypes.shape(),
}

export default ReimbursementPoint
