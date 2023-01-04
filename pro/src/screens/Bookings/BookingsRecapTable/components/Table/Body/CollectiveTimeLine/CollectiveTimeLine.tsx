import React from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { BOOKING_STATUS } from 'core/Bookings'
import {
  ReactComponent as IcoPen,
  ReactComponent as ExternalLinkIcon,
} from 'icons/ico-external-site-filled.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Timeline from 'ui-kit/Timeline'
import { TimelineStepType } from 'ui-kit/Timeline/Timeline'
import { getDateToFrenchText } from 'utils/date'

import styles from './CollectiveTimeLine.module.scss'

export interface ICollectiveBookingDetailsProps {
  bookingRecap: CollectiveBookingResponseModel
}

const CollectiveTimeLine = ({
  bookingRecap,
}: ICollectiveBookingDetailsProps) => {
  const bookingDate = getDateToFrenchText(bookingRecap.booking_date)
  const confirmationDate = getDateToFrenchText(
    bookingRecap.booking_confirmation_date
  )
  const confirmationLimitDate = getDateToFrenchText(
    bookingRecap.booking_confirmation_limit_date
  )
  const cancellationLimitDate = getDateToFrenchText(
    bookingRecap.booking_cancellation_limit_date
  )
  const eventDate = getDateToFrenchText(
    bookingRecap.stock.event_beginning_datetime
  )

  const pendingStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-passed']}>
          Préreservée par l'établissement scolaire
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
          Réservée par l'établissement scolaire
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
              to: `/offre/${bookingRecap.stock.offer_identifier}/collectif/stocks/edition`,
              isExternal: false,
            }}
            Icon={IcoPen}
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
          15 jours avant la date de l’événement, l’établissement scolaire ne
          peut plus annuler. De votre côté, vous pouvez annuler la réservation
          jusqu’à 48 heures après la date de l’événement.
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
          Nous espérons que votre événement s’est bien déroulé.
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: 'https://aide.passculture.app/hc/fr/articles/4405297381788--Acteurs-Culturels-Que-faire-si-le-groupe-scolaire-n-est-pas-au-complet-ou-doit-annuler-sa-participation-',
              isExternal: true,
            }}
            Icon={ExternalLinkIcon}
          >
            Modifier la date limite de réservation
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
          À compter du jour de l'événement, le virement sera exécuté dans un
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

  const statusSteps = [
    {
      status: BOOKING_STATUS.PENDING,
      steps: [
        pendingStep,
        waitingBookingStep,
        disabledConfirmedStep,
        disabledEndedStep,
        disabledReimbursedStep,
      ],
    },
    {
      status: BOOKING_STATUS.BOOKED,
      steps: [
        pendingStep,
        confirmationStep,
        waitingConfirmedStep,
        disabledEndedStep,
        disabledReimbursedStep,
      ],
    },
    {
      status: BOOKING_STATUS.CONFIRMED,
      steps: [
        pendingStep,
        confirmationStep,
        confirmedStep,
        waitingEndedStep,
        disabledReimbursedStep,
      ],
    },
    {
      status: BOOKING_STATUS.VALIDATED,
      steps: [
        pendingStep,
        confirmationStep,
        confirmedStep,
        endedStep,
        waitingReimbursedStep,
      ],
    },
    {
      status: BOOKING_STATUS.REIMBURSED,
      steps: [
        pendingStep,
        confirmationStep,
        confirmedStep,
        passedEndedStep,
        reimbursedStep,
      ],
    },
  ]
  const steps = statusSteps.find(
    x => x.status == bookingRecap.booking_status
  )?.steps
  return <div>{steps && <Timeline steps={steps} />}</div>
}

export default CollectiveTimeLine
