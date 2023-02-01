import React from 'react'

import {
  CollectiveBookingBankInformationStatus,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { CollectiveBookingCancellationReasons } from 'apiClient/v1/models/CollectiveBookingCancellationReasons'
import { BOOKING_STATUS } from 'core/Bookings'
import { ExternalLinkIcon, PenIcon } from 'icons'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Timeline from 'ui-kit/Timeline'
import { ITimelineStep, TimelineStepType } from 'ui-kit/Timeline/Timeline'
import { getDateToFrenchText } from 'utils/date'

import styles from './CollectiveTimeLine.module.scss'

export interface ICollectiveBookingDetailsProps {
  bookingRecap: CollectiveBookingResponseModel
  bookingDetails: CollectiveBookingByIdResponseModel
}

const cancellationReasonTitle = (
  bookingRecap: CollectiveBookingResponseModel
): string | null => {
  if (!bookingRecap.bookingCancellationReason) {
    return null
  }
  switch (bookingRecap.bookingCancellationReason) {
    case CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE:
    case CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER:
      return 'Annulé par l’établisssement scolaire'
    case CollectiveBookingCancellationReasons.OFFERER:
    case CollectiveBookingCancellationReasons.BENEFICIARY:
      return 'Vous avez annulé la réservation'
    case CollectiveBookingCancellationReasons.EXPIRED:
      return 'Annulé automatiquement'
    default:
      throw new Error('Invalid cancellation reason')
  }
}

const CollectiveTimeLine = ({
  bookingRecap,
  bookingDetails,
}: ICollectiveBookingDetailsProps) => {
  const bookingDate = getDateToFrenchText(bookingRecap.bookingDate)
  const confirmationDate =
    bookingRecap.bookingConfirmationDate &&
    getDateToFrenchText(bookingRecap.bookingConfirmationDate)
  const confirmationLimitDate = getDateToFrenchText(
    bookingRecap.bookingConfirmationLimitDate
  )
  const cancellationLimitDate = getDateToFrenchText(
    bookingRecap.bookingCancellationLimitDate
  )
  const eventDate = getDateToFrenchText(
    bookingRecap.stock.eventBeginningDatetime
  )
  const cancelledDate = getDateToFrenchText(
    bookingRecap.bookingStatusHistory[
      bookingRecap.bookingStatusHistory.length - 1
    ].date
  )
  const pendingStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Préreservée par l’établissement scolaire
        </div>
        <div>{bookingDate}</div>
      </>
    ),
  }
  const confirmationStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Réservée par l’établissement scolaire
        </div>
        <div>{confirmationDate}</div>
      </>
    ),
  }
  const confirmedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Réservation confirmée
        </div>
        <div>
          {cancellationLimitDate}
          <br />
          La réservation n’est plus annulable par l’établissement scolaire.
        </div>
      </>
    ),
  }
  const waitingBookingStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          En attente de réservation
        </div>
        <div className={styles['timeline-infobox']}>
          <div className={styles['timeline-infobox-text']}>
            L’établissement scolaire doit confirmer la préréservation{' '}
            <span className={styles['timeline-infobox-accent']}>
              avant le {confirmationLimitDate}
            </span>
            , autrement celle-ci sera automatiquement annulée.
          </div>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: `/offre/${bookingRecap.stock.offerIdentifier}/collectif/stocks/edition`,
              isExternal: false,
            }}
            Icon={PenIcon}
          >
            Modifier la date limite de réservation
          </ButtonLink>
        </div>
      </>
    ),
  }
  const waitingConfirmedStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Réservation en cours de confirmation
        </div>
        <div>
          À partir du {cancellationLimitDate.toString()}, la réservation ne sera
          plus annulable par l’établissement scolaire. <br />
          <br />
          15 jours avant la date de l’évènement, l’établissement scolaire ne
          peut plus annuler. De votre côté, vous pouvez annuler la réservation
          jusqu’à 48 heures après la date de l’évènement.
        </div>
      </>
    ),
  }
  const disabledConfirmedStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Réservation confirmée
      </div>
    ),
  }
  const endedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Jour J : réservation terminée
        </div>
        <div>
          {eventDate}
          <br />
          <br />
          Nous espérons que votre évènement s’est bien déroulé.
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: 'https://aide.passculture.app/hc/fr/articles/4405297381788--Acteurs-Culturels-Que-faire-si-le-groupe-scolaire-n-est-pas-au-complet-ou-doit-annuler-sa-participation-',
              isExternal: true,
            }}
            Icon={ExternalLinkIcon}
          >
            Je rencontre un problème à cette étape
          </ButtonLink>
        </div>
      </>
    ),
  }
  const waitingEndedStep = {
    type: TimelineStepType.WAITING,
    content: (
      <div className={styles['timeline-step-title']}>
        Jour J : réservation terminée
      </div>
    ),
  }
  const disabledEndedStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Jour J : réservation terminée
      </div>
    ),
  }
  const passedEndedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Jour J : réservation terminée
        </div>
        <div>{eventDate}</div>
      </>
    ),
  }

  const reimbursedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Remboursement effectué
        </div>
        <div>{}</div>
      </>
    ),
  }
  const waitingReimbursedStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Remboursement à venir
        </div>
        <div>
          À compter du jour de l'évènement, le virement sera exécuté dans un
          délai de 2 à 3 semaines.
        </div>
      </>
    ),
  }
  const disabledReimbursedStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Remboursement effectué
      </div>
    ),
  }

  const cancelledStep = {
    type: TimelineStepType.ERROR,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          {cancellationReasonTitle(bookingRecap)}
        </div>
        <div>
          {cancelledDate}
          <br />
          <br />
          {bookingRecap.bookingCancellationReason ===
            CollectiveBookingCancellationReasons.EXPIRED &&
            `L’établissement scolaire n’a pas confirmé la préréservation avant la date limite de réservation fixée au ${cancellationLimitDate}.`}
          <div>
            Votre réservation a été annulée. Votre offre est de nouveau visible
            sur ADAGE.
          </div>
        </div>
      </>
    ),
  }
  const waitingMissingBankInfo = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Remboursement en attente
        </div>
        <div>
          Vous devez renseigner des coordonnées bancaires pour percevoir le
          remboursement.
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: `/structures/${bookingDetails.offererId}/lieux/${bookingDetails.venueId}?modification#reimbursement-section`,
            isExternal: false,
          }}
          Icon={ExternalLinkIcon}
          className={styles['button-important']}
        >
          Renseigner mes coordonnées bancaires
        </ButtonLink>
      </>
    ),
  }

  const waitingPendingBankInfo = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Remboursement en attente
        </div>
        <div>
          Les coordonnées bancaires de votre lieu sont en cours de validation
          par notre service financier. Vos remboursements seront rétroactifs une
          fois vos coordonnées bancaires ajoutées.
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: `https://www.demarches-simplifiees.fr/dossiers/${bookingDetails.venueDMSApplicationId}`,
            isExternal: true,
          }}
          Icon={ExternalLinkIcon}
        >
          Voir le dossier en cours
        </ButtonLink>
      </>
    ),
  }

  const arrayHistoryStep: Array<ITimelineStep> =
    bookingRecap.bookingStatusHistory.map(el => {
      switch (el.status) {
        case BOOKING_STATUS.PENDING:
          return pendingStep
        case BOOKING_STATUS.BOOKED:
          return confirmationStep
        case BOOKING_STATUS.CONFIRMED:
          return confirmedStep
        case BOOKING_STATUS.VALIDATED:
          return passedEndedStep
        case BOOKING_STATUS.REIMBURSED:
          return reimbursedStep
        case BOOKING_STATUS.CANCELLED:
          return cancelledStep
        default:
          throw new Error('Invalid booking history status')
      }
    })

  let lastValidatedStep = waitingReimbursedStep
  if (
    bookingDetails.bankInformationStatus ==
    CollectiveBookingBankInformationStatus.DRAFT
  ) {
    lastValidatedStep = waitingPendingBankInfo
  }
  if (
    bookingDetails.bankInformationStatus ==
    CollectiveBookingBankInformationStatus.MISSING
  ) {
    lastValidatedStep = waitingMissingBankInfo
  }

  switch (bookingRecap.bookingStatus) {
    case BOOKING_STATUS.PENDING:
      return (
        <Timeline
          steps={[
            pendingStep,
            waitingBookingStep,
            disabledConfirmedStep,
            disabledEndedStep,
            disabledReimbursedStep,
          ]}
        />
      )
    case BOOKING_STATUS.BOOKED:
      return (
        <Timeline
          steps={[
            pendingStep,
            confirmationStep,
            waitingConfirmedStep,
            disabledEndedStep,
            disabledReimbursedStep,
          ]}
        />
      )
    case BOOKING_STATUS.CONFIRMED:
      return (
        <Timeline
          steps={[
            pendingStep,
            confirmationStep,
            confirmedStep,
            waitingEndedStep,
            disabledReimbursedStep,
          ]}
        />
      )
    case BOOKING_STATUS.VALIDATED:
      return (
        <Timeline
          steps={[
            pendingStep,
            confirmationStep,
            confirmedStep,
            endedStep,
            lastValidatedStep,
          ]}
        />
      )
    case BOOKING_STATUS.REIMBURSED:
      return (
        <Timeline
          steps={[
            pendingStep,
            confirmationStep,
            confirmedStep,
            passedEndedStep,
            reimbursedStep,
          ]}
        />
      )
    case BOOKING_STATUS.CANCELLED:
      return <Timeline steps={arrayHistoryStep} />
    default:
      throw new Error('Invalid booking status')
  }
}

export default CollectiveTimeLine
