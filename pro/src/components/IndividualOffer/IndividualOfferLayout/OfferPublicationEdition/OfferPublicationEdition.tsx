import { useState } from 'react'
import { mutate } from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useNotification } from 'commons/hooks/useNotification'
import { serializeDateTimeToUTCFromLocalDepartment } from 'components/IndividualOffer/StocksEventEdition/serializers'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import styles from './OfferPublicationEdition.module.scss'
import { OfferPublicationEditionForm } from './OfferPublicationEditionForm/OfferPublicationEditionForm'
import { EventPublicationEditionFormValues } from './OfferPublicationEditionForm/types'
import { OfferPublicationEditionTags } from './OfferPublicationEditionTags/OfferPublicationEditionTags'

export type OfferPublicationEditionProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function getPatchOfferPayloadFromFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  values: EventPublicationEditionFormValues
) {
  const formattedPublicationDate =
    values.publicationDate && values.publicationTime
      ? serializeDateTimeToUTCFromLocalDepartment(
          values.publicationDate,
          values.publicationTime,
          getDepartmentCode(offer)
        )
      : undefined

  const formattedBookabilityDate =
    values.bookingAllowedDate && values.bookingAllowedTime
      ? serializeDateTimeToUTCFromLocalDepartment(
          values.bookingAllowedDate,
          values.bookingAllowedTime,
          getDepartmentCode(offer)
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
}: OfferPublicationEditionProps) {
  const notify = useNotification()

  const [isDialogOpen, setIsDialogOpen] = useState(false)

  async function onSubmit(values: EventPublicationEditionFormValues) {
    try {
      await api.patchOffer(
        offer.id,
        getPatchOfferPayloadFromFormValues(offer, values)
      )

      await mutate([GET_OFFER_QUERY_KEY, offer.id])

      setIsDialogOpen(false)
    } catch {
      notify.error('Une erreur est survenue lors de la modification de l’offre')
    }
  }

  return (
    <div className={styles['container']}>
      <OfferPublicationEditionTags offer={offer} />
      <DialogBuilder
        trigger={
          <Button variant={ButtonVariant.TERNARY} icon={fullEditIcon}>
            Modifier
          </Button>
        }
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        title="Publication et réservation"
        variant="drawer"
      >
        <OfferPublicationEditionForm offer={offer} onSubmit={onSubmit} />
      </DialogBuilder>
    </div>
  )
}
