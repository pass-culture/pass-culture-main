import React, { useCallback, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import Dialog from 'components/Dialog/Dialog/Dialog'
import ReimbursmentPointDialog from 'components/ReimbursementPointDialog/ReimbursmentPointDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { serializeVenueApi } from 'core/Venue/adapters/getVenueAdapter/serializers'
import { Venue } from 'core/Venue/types'
import useAnalytics from 'hooks/useAnalytics'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import ApplicationBanner from 'pages/Offerers/Offerer/VenueV1/fields/ApplicationBanner'
import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form'
import { Title } from 'ui-kit/index'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './ReimbursementPoint.module.scss'

interface ReimbursementPointV2 {
  initialVenue: Venue
  isCreatingVenue?: boolean
  offerer: GetOffererResponseModel
  venueHasPricingPoint?: boolean
}
type ReimbursementPointOptions = {
  key: string
  displayName: string
  id: number
}
type ReimbursementPoint = {
  iban: string
  venueName: string
}

const ReimbursementPoint = ({
  offerer,
  initialVenue,
  isCreatingVenue = false,
  venueHasPricingPoint,
}: ReimbursementPointV2) => {
  const [reimbursementPointOptions, setReimbursementPointOptions] =
    useState<Array<ReimbursementPointOptions>>()
  const [venueReimbursementPoint, setVenueReimbursementPoint] = useState<any>(
    []
  )
  const [isLoading, setIsLoading] = useState(true)
  const [isNoSiretDialogOpen, setIsNoSiretDialogOpen] = useState(false)
  const [
    hasPendingBankInformationApplication,
    setHasPendingBankInformationApplication,
  ] = useState<boolean | null | undefined>(false)
  const [hasAlreadyAddReimbursementPoint, setHasAlreadyAddReimbursementPoint] =
    useState<object>()
  const [venue, setVenue] = useState(initialVenue)
  const [isDmsDialogOpen, setIsDmsDialogOpen] = useState(false)

  const reimbursementPointDisplayName = (
    reimbursementPoint: ReimbursementPoint
  ) =>
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
    setVenue(serializeVenueApi(venueRequest))
  }, [])

  useEffect(() => {
    async function loadReimbursementPoints(offererId: number) {
      const reimbursementPointsResponse =
        await api.getAvailableReimbursementPoints(offererId)
      let venueReimbursementPointResponse = null
      if (venue.reimbursementPointId) {
        venueReimbursementPointResponse = reimbursementPointsResponse.find(
          (reimbursementPoint) =>
            reimbursementPoint.venueId === venue.reimbursementPointId
        )
      }
      setHasAlreadyAddReimbursementPoint(
        reimbursementPointsResponse.find(
          (reimbursementPoint) => reimbursementPoint.venueId === venue.id
        )
      )

      setVenueReimbursementPoint(venueReimbursementPointResponse)
      setReimbursementPointOptions(
        reimbursementPointsResponse.map((reimbursementPoint) => ({
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
    loadReimbursementPoints(offerer.id)
  }, [isCreatingVenue, offerer.id, venue])
  const { logEvent } = useAnalytics()

  const onCancelNoSiretDialog = () => {
    setIsNoSiretDialogOpen(false)
    logEvent?.(Events.CLICKED_NO_PRICING_POINT_SELECTED_YET, {
      from: location.pathname,
    })
  }

  if (isLoading) {
    return <Spinner />
  }

  return (
    <div className="section reimbursement-point-section">
      <Title as="h3" className="sub-title" level={4}>
        Coordonnées bancaires
      </Title>
      {hasPendingBankInformationApplication &&
      venue.demarchesSimplifieesApplicationId ? (
        <ApplicationBanner
          applicationId={venue.demarchesSimplifieesApplicationId}
        />
      ) : (
        <>
          {isNoSiretDialogOpen && (
            <Dialog
              icon={strokeWarningIcon}
              title="Vous devez sélectionner un lieu avec SIRET pour ajouter de nouvelles coordonnées bancaires"
              explanation="Sélectionner un lieu avec SIRET parmi la liste puis valider votre sélection."
              onCancel={onCancelNoSiretDialog}
            >
              <Button
                onClick={onCancelNoSiretDialog}
                className={styles['dialog-confirm-button']}
              >
                J’ai compris
              </Button>
            </Dialog>
          )}
          <p className={styles['section-description']}>
            Ces coordonnées bancaires seront utilisées pour les remboursements
            des offres éligibles de ce lieu.
          </p>
          {!venueReimbursementPoint && (
            <div className={styles['add-reimbursement-point-section']}>
              <Button
                id="add-new-reimbursement-point"
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  openDMSApplication()
                  logEvent?.(Events.CLICKED_ADD_BANK_INFORMATIONS, {
                    from: location.pathname,
                  })
                }}
                type="button"
              >
                Ajouter des coordonnées bancaires
              </Button>
            </div>
          )}
          {!venueReimbursementPoint && !!reimbursementPointOptions?.length && (
            <p className={styles['or-separator']}>ou</p>
          )}
          {isDmsDialogOpen && (
            <ReimbursmentPointDialog
              closeDialog={closeDmsDialog}
              dmsToken={venue.dmsToken}
            />
          )}
          {!!reimbursementPointOptions?.length && (
            <div className={styles['field-select']}>
              {!venueReimbursementPoint && (
                <p className={styles['select-description']}>
                  <b>Sélectionner</b> des coordonnées bancaires parmi celles
                  déjà existantes dans votre structure :
                </p>
              )}

              <Select
                id="reimbursementPointId"
                name="reimbursementPointId"
                className={styles['select-input']}
                disabled={!venueHasPricingPoint}
                label="Coordonnées bancaires"
                hideFooter
                defaultValue={
                  venueReimbursementPoint ? venueReimbursementPoint.venueId : ''
                }
                options={[
                  {
                    value: '',
                    label: 'Sélectionner des coordonnées dans la liste',
                  },
                  ...reimbursementPointOptions.map((option) => ({
                    value: option.id,
                    label: option.displayName,
                  })),
                ]}
              />
              {venueReimbursementPoint && (
                <div className={styles['add-reimbursement-point-section']}>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    id="modify-new-reimbursement-point"
                    onClick={openDMSApplication}
                    type="button"
                  >
                    {modifyReimbursementPointLabel()}
                  </Button>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ReimbursementPoint
