import { useState } from 'react'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetIndividualOfferWithAddressResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { serializeDateTimeToUTCFromLocalDepartment } from '@/commons/utils/timezone'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import fullEditIcon from '@/icons/full-edit.svg'

import styles from './OfferPublicationEdition.module.scss'
import {
  OFFER_PUBLICATION_EDITION_FORM_ID,
  OfferPublicationEditionForm,
} from './OfferPublicationEditionForm/OfferPublicationEditionForm'
import type { EventPublicationEditionFormValues } from './OfferPublicationEditionForm/types'
import { OfferPublicationEditionTags } from './OfferPublicationEditionTags/OfferPublicationEditionTags'

export type OfferPublicationEditionProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function getPatchOfferPayloadFromFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  venue: GetVenueResponseModel,
  values: EventPublicationEditionFormValues
) {
  const formattedPublicationDate =
    values.publicationDate && values.publicationTime
      ? serializeDateTimeToUTCFromLocalDepartment(
          values.publicationDate,
          values.publicationTime,
          getDepartmentCode(offer, venue)
        )
      : undefined

  const formattedBookabilityDate =
    values.bookingAllowedDate && values.bookingAllowedTime
      ? serializeDateTimeToUTCFromLocalDepartment(
          values.bookingAllowedDate,
          values.bookingAllowedTime,
          getDepartmentCode(offer, venue)
        )
      : undefined

  const newPublicationDateTime =
    values.publicationMode === 'later' ? formattedPublicationDate : 'now'

  const newBookingAllowedDateTime =
    values.bookingAllowedMode === 'later' ? formattedBookabilityDate : null

  return {
    publicationDatetime: values.isPaused ? null : newPublicationDateTime,
    bookingAllowedDatetime: values.isPaused ? null : newBookingAllowedDateTime,
  }
}

export function OfferPublicationEdition({
  offer,
}: Readonly<OfferPublicationEditionProps>) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const snackBar = useSnackBar()

  const [isDialogOpen, setIsDialogOpen] = useState(false)

  async function onSubmit(values: EventPublicationEditionFormValues) {
    try {
      await mutate(
        [GET_OFFER_QUERY_KEY, offer.id],
        api.patchOffer({
          path: { offer_id: offer.id },
          body: getPatchOfferPayloadFromFormValues(
            offer,
            selectedPartnerVenue,
            values
          ),
        }),
        { revalidate: false }
      )

      setIsDialogOpen(false)
    } catch {
      snackBar.error(
        'Une erreur est survenue lors de la modification de l’offre'
      )
    }
  }

  return (
    <div className={styles['container']}>
      <OfferPublicationEditionTags offer={offer} />
      <Button
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        size={ButtonSize.SMALL}
        icon={fullEditIcon}
        label="Gérer la publication"
        disabled={withVenueHelpers(selectedPartnerVenue).isClosed}
        onClick={() => setIsDialogOpen(true)}
      />
      <DetailedModal
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        title="Publication et réservation"
        primaryAction={
          <Button
            type="submit"
            form={OFFER_PUBLICATION_EDITION_FORM_ID}
            variant={ButtonVariant.PRIMARY}
            label="Enregistrer"
          />
        }
        secondaryAction={
          <Button
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            onClick={() => setIsDialogOpen(false)}
            label="Annuler"
          />
        }
      >
        {isDialogOpen && (
          <OfferPublicationEditionForm offer={offer} onSubmit={onSubmit} />
        )}
      </DetailedModal>
    </div>
  )
}
