import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Field } from 'react-final-form'

import { api } from 'apiClient/api'
import Spinner from 'components/layout/Spinner'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import InfoDialog from 'new_components/InfoDialog'
import ReimbursmentPointDialog from 'new_components/reimbursementPointDialog'
import { Title } from 'ui-kit'

import ApplicationBanner from '../ApplicationBanner'

import styles from './ReimbursementPoint.module.scss'

const ReimbursementPoint = ({
  readOnly,
  offerer,
  initialVenue,
  isCreatingVenue,
  venueHasPricingPoint,
}) => {
  const [reimbursementPointOptions, setReimbursementPointOptions] = useState([])
  const [venueReimbursementPoint, setVenueReimbursementPoint] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isNoSiretDialogOpen, setIsNoSiretDialogOpen] = useState(false)
  const [
    hasPendingBankInformationApplication,
    setHasPendingBankInformationApplication,
  ] = useState(false)
  const [hasAlreadyAddReimbursementPoint, setHasAlreadyAddReimbursementPoint] =
    useState(false)
  const [venue, setVenue] = useState(initialVenue)

  const reimbursementPointDisplayName = reimbursementPoint =>
    reimbursementPoint
      ? `${reimbursementPoint.venueName} - ${reimbursementPoint.iban}`
      : ''

  const modifyReimbursementPointLabel = useCallback(() => {
    return hasAlreadyAddReimbursementPoint
      ? 'Modifier mes coordonnées bancaires'
      : 'Ajouter des coordonnées bancaires'
  }, [hasAlreadyAddReimbursementPoint])

  const openDMSApplication = useCallback(() => {
    if (venueHasPricingPoint || venue.siret) {
      setIsDmsDialogOpen(true)
    } else {
      setIsNoSiretDialogOpen(true)
    }
  }, [venueHasPricingPoint])

  const closeDmsDialog = useCallback(async () => {
    setIsDmsDialogOpen(false)
    const venueRequest = await api.getVenue(venue.id)
    setVenue(venueRequest)
  }, [])
  const [isDmsDialogOpen, setIsDmsDialogOpen] = useState(false)
  useEffect(() => {
    async function loadReimbursementPoints(offererId) {
      const reimbursementPointsResponse =
        await api.getAvailableReimbursementPoints(offererId)
      let venueReimbursementPointResponse = null
      if (venue.reimbursementPointId) {
        venueReimbursementPointResponse = reimbursementPointsResponse.find(
          reimbursementPoint =>
            reimbursementPoint.venueId === venue.reimbursementPointId
        )
      }
      setHasAlreadyAddReimbursementPoint(
        reimbursementPointsResponse.find(
          reimbursementPoint =>
            reimbursementPoint.venueId === venue.nonHumanizedId
        )
      )

      setVenueReimbursementPoint(venueReimbursementPointResponse)
      setReimbursementPointOptions(
        reimbursementPointsResponse.map(reimbursementPoint => ({
          key: `venue-reimbursement-point-${reimbursementPoint.venueId}`,
          displayName: reimbursementPointDisplayName(reimbursementPoint),
          id: reimbursementPoint.venueId,
        }))
      )
      setHasPendingBankInformationApplication(
        venue.hasPendingBankInformationApplication
      )
      setIsLoading(false)
    }
    loadReimbursementPoints(offerer.nonHumanizedId)
  }, [isCreatingVenue, offerer.id, readOnly, venue])
  const { logEvent } = useAnalytics()
  if (isLoading) return <Spinner />

  return (
    <div className="section reimbursement-point-section">
      <div className="main-list-title">
        <Title as="h2" level={4} className={styles['sub-title-text']}>
          Coordonnées bancaires
        </Title>
      </div>
      {hasPendingBankInformationApplication ? (
        <ApplicationBanner
          applicationId={venue.demarchesSimplifieesApplicationId}
        />
      ) : (
        <>
          {isNoSiretDialogOpen && (
            <InfoDialog
              buttonText="J'ai compris"
              iconName="ico-info-wrong"
              title="Vous devez sélectionner un lieu avec SIRET pour ajouter de nouvelles coordonnées bancaires"
              subTitle="Sélectionner un lieu avec SIRET parmi la liste puis valider votre sélection."
              closeDialog={() => {
                setIsNoSiretDialogOpen(false)
                logEvent?.(Events.CLICKED_NO_PRICING_POINT_SELECTED_YET, {
                  from: location.pathname,
                })
              }}
            />
          )}
          <p className={styles['section-description']}>
            Ces coordonnées bancaires seront utilisées pour les remboursements
            des offres éligibles de ce lieu.
          </p>
          {!venueReimbursementPoint && (
            <div className={styles['add-reimbursement-point-section']}>
              <button
                className="secondary-button"
                id="add-new-reimbursement-point"
                onClick={() => {
                  openDMSApplication()
                  logEvent?.(Events.CLICKED_ADD_BANK_INFORMATIONS, {
                    from: location.pathname,
                  })
                }}
                type="button"
              >
                Ajouter des coordonnées bancaires
              </button>
            </div>
          )}
          {!venueReimbursementPoint && !!reimbursementPointOptions.length && (
            <p className={styles['or-separator']}>ou</p>
          )}
          {isDmsDialogOpen && (
            <ReimbursmentPointDialog
              closeDialog={closeDmsDialog}
              buttonAction={openDMSApplication}
              dmsToken={venue.dmsToken}
            />
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
                  name="reimbursementPointId"
                  disabled={readOnly || !venueHasPricingPoint}
                  initialValue={
                    venueReimbursementPoint
                      ? venueReimbursementPoint.venueId
                      : null
                  }
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
              {venueReimbursementPoint && (
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
}

ReimbursementPoint.defaultProps = {
  initialVenue: {},
  isCreatingVenue: false,
  readOnly: false,
}
ReimbursementPoint.propTypes = {
  initialVenue: PropTypes.shape(),
  isCreatingVenue: PropTypes.bool,
  offerer: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
}

export default ReimbursementPoint
