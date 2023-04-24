import React, { useCallback, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import InfoDialog from 'components/InfoDialog'
import ReimbursmentPointDialog from 'components/reimbursementPointDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { IVenue } from 'core/Venue'
import { serializeVenueApi } from 'core/Venue/adapters/getVenueAdapter/serializers'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as IcoWarningGrey } from 'icons/ico-warning-grey.svg'
import ApplicationBanner from 'pages/Offerers/Offerer/VenueV1/fields/ApplicationBanner'
import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form'
import { Title } from 'ui-kit/index'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './ReimbursementPoint.module.scss'

interface IReimbursementPointV2 {
  initialVenue: IVenue
  isCreatingVenue?: boolean
  offerer: GetOffererResponseModel
  readOnly: boolean
  venueHasPricingPoint?: boolean
}
export type IReimbursementPointOptions = {
  key: string
  displayName: string
  id: number
}
type IReimbursementPoint = {
  iban: string
  venueName: string
}
const ReimbursementPoint = ({
  readOnly = false,
  offerer,
  initialVenue,
  isCreatingVenue = false,
  venueHasPricingPoint,
}: IReimbursementPointV2) => {
  const [reimbursementPointOptions, setReimbursementPointOptions] =
    useState<Array<IReimbursementPointOptions>>()
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
    reimbursementPoint: IReimbursementPoint
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
    const venueRequest = await api.getVenue(venue.nonHumanizedId)
    setVenue(serializeVenueApi(venueRequest))
  }, [])

  useEffect(() => {
    async function loadReimbursementPoints(offererId: number) {
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
            <InfoDialog
              buttonText="J'ai compris"
              componentIcon={<IcoWarningGrey />}
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
                disabled={readOnly || !venueHasPricingPoint}
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
                  ...reimbursementPointOptions.map(option => ({
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
