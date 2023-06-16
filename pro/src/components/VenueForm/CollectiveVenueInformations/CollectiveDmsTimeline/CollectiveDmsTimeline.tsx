import React from 'react'

import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { InfoWrongIcon } from 'icons'
import { ReactComponent as FullEdit } from 'icons/full-edit.svg'
import { ReactComponent as FullLink } from 'icons/full-link.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Timeline, { TimelineStepType } from 'ui-kit/Timeline/Timeline'
import { getDateToFrenchText } from 'utils/date'

import styles from './CollectiveDmsTimeline.module.scss'

const CollectiveDmsTimeline = ({
  collectiveDmsApplication,
  hasAdageId,
  hasAdageIdForMoreThan30Days,
  adageInscriptionDate,
  offererId,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId: boolean
  hasAdageIdForMoreThan30Days: boolean
  adageInscriptionDate: string | null
  offererId: number
}) => {
  const collectiveDmsApplicationLink = `https://www.demarches-simplifiees.fr/dossiers/${collectiveDmsApplication.application}/messagerie`
  const collectiveVenueInformationsLink = `/structures/${offererId}/lieux/${collectiveDmsApplication.venueId}/eac`
  const collectiveDmsContactSupport =
    'https://aide.passculture.app/hc/fr/articles/8491401511708'

  const buildDate =
    collectiveDmsApplication.buildDate &&
    getDateToFrenchText(collectiveDmsApplication.buildDate)

  const instructionDate =
    collectiveDmsApplication.instructionDate &&
    getDateToFrenchText(collectiveDmsApplication.instructionDate)

  const processingDate =
    collectiveDmsApplication.processingDate &&
    getDateToFrenchText(collectiveDmsApplication.processingDate)

  const adageDate =
    adageInscriptionDate && getDateToFrenchText(adageInscriptionDate)
  const { logEvent } = useAnalytics()
  const logClickOnDmsLink = (status: DMSApplicationstatus) => {
    logEvent?.(Events.CLICKED_EAC_DMS_LINK, {
      from: location.pathname,
      dmsApplicationStatus: status,
    })
  }

  const successSubmittedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre dossier a été déposé
        </div>
        <div>{buildDate}</div>
      </>
    ),
  }

  const confirmationSubmittedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre dossier a été déposé
        </div>
        <div>
          {buildDate}
          <br />
          <div className={styles['timeline-step-description']}>
            Votre demande de référencement a bien été déposée. Elle sera étudiée
            par les services du Ministère de l’Education Nationale et de la
            Culture lors d’une commission mensuelle. En fonction du nombre de
            dossiers en cours, cela peut prendre jusqu’à 3 mois.
          </div>
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={FullLink}
          onClick={() =>
            logClickOnDmsLink(DMSApplicationstatus.EN_CONSTRUCTION)
          }
        >
          Consulter ma messagerie sur Démarches Simplifiées
        </ButtonLink>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsContactSupport,
            isExternal: true,
          }}
          Icon={FullLink}
        >
          Contacter les services des Ministères de l’Education Nationale et de
          la Culture
        </ButtonLink>
      </>
    ),
  }

  const waitingInstructionStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Votre dossier est en cours d'instruction
        </div>
        <div>
          {instructionDate}
          <br />
          <div className={styles['timeline-step-description']}>
            Votre dossier est en cours d’instruction par la commission régionale
            DAAC et DRAC où est déclaré votre siège social. Si votre dossier
            concerne un établissement public, il est traité par le Ministère de
            la Culture.
          </div>
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={FullLink}
          onClick={() => logClickOnDmsLink(DMSApplicationstatus.EN_INSTRUCTION)}
        >
          Consulter ma messagerie sur Démarches Simplifiées
        </ButtonLink>
      </>
    ),
  }

  const successInstructionStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre dossier est passé en instruction
        </div>
        <div>{instructionDate}</div>
      </>
    ),
  }

  const successDoneReferencement = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre demande de référencement a été acceptée
        </div>
        <div>
          {processingDate}
          <br />
          <div className={styles['timeline-step-description']}>
            Votre lieu sera bientôt ajouté dans ADAGE par le Ministère de
            l’Éducation Nationale. Cela peut prendre quelques jours.
          </div>
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={FullLink}
          onClick={() => logClickOnDmsLink(DMSApplicationstatus.ACCEPTE)}
        >
          Consulter ma messagerie sur Démarches Simplifiées
        </ButtonLink>
      </>
    ),
  }

  const disabledInstructionStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Votre dossier est passé en instruction
      </div>
    ),
  }
  const disabledDoneStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Votre dossier a été traité
      </div>
    ),
  }

  const waitingAdageStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Votre lieu est en cours d’ajout dans ADAGE
        </div>
        <div className={styles['timeline-step-description']}>
          Une fois votre lieu ajouté dans ADAGE par le Ministère de l’Education
          Nationale, vous pourrez renseigner vos informations à destination des
          enseignants et créer des offres à destination des scolaires.
        </div>
      </>
    ),
  }

  const successAdageStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre lieu a été ajouté dans ADAGE par le Ministère de l’Education
          Nationale
        </div>
        <div>{adageDate}</div>
        <div className={styles['timeline-infobox']}>
          <div className={styles['timeline-infobox-text']}>
            Vous pouvez désormais créer des offres collectives ! Nous vous
            invitons à vérifier les informations de votre lieu qui sont
            désormais visibles sur ADAGE par les enseignants et chefs
            d’établissements.
          </div>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveVenueInformationsLink,
              isExternal: true,
            }}
            Icon={FullEdit}
          >
            Vérifier les informations de mon lieu
          </ButtonLink>
        </div>
      </>
    ),
  }

  const disabledAcceptedAdageStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Votre lieu a été ajouté dans ADAGE
      </div>
    ),
  }

  const refusedByDms = (
    <>
      <div className={styles['refused-state']}>
        <InfoWrongIcon className={styles['refused-state-icon']} />
        <span>Votre demande de référencement a été refusée</span>
      </div>
      <div>
        <div className={styles['timeline-step-description']}>
          Votre dossier a été refusé le {processingDate} par la commission
          régionale DAAC et DRAC de la région où est déclaré votre siège social.
          Nous vous invitons à consulter votre messagerie sur Démarches
          Simplifiées afin d’en savoir plus sur les raisons de ce refus.
        </div>
        <div className={styles['timeline-step-button']}>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveDmsApplicationLink,
              isExternal: true,
            }}
            Icon={FullLink}
            onClick={() => logClickOnDmsLink(DMSApplicationstatus.REFUSE)}
          >
            Consulter ma messagerie sur Démarches Simplifiées
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveDmsContactSupport,
              isExternal: true,
            }}
            Icon={FullLink}
          >
            Contacter les services des Ministères de l’Education Nationale et de
            la Culture
          </ButtonLink>
        </div>
      </div>
    </>
  )
  const droppedByDms = (
    <>
      <div className={styles['refused-state']}>
        <InfoWrongIcon className={styles['refused-state-icon']} />
        <span>Votre demande de référencement a été classée sans suite</span>
      </div>
      <div className={styles['timeline-step-description']}>
        Nous vous invitons à consulter votre messagerie sur Démarches
        Simplifiées afin d’en savoir plus.
        <div className={styles['timeline-step-button']}>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveDmsApplicationLink,
              isExternal: true,
            }}
            Icon={FullLink}
            onClick={() => logClickOnDmsLink(DMSApplicationstatus.SANS_SUITE)}
          >
            Consulter ma messagerie sur Démarches Simplifiées
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveDmsContactSupport,
              isExternal: true,
            }}
            Icon={FullLink}
          >
            Contacter les services des Ministères de l’Education Nationale et de
            la Culture
          </ButtonLink>
        </div>
      </div>
    </>
  )
  if (
    hasAdageId &&
    collectiveDmsApplication.state !== DMSApplicationstatus.ACCEPTE
  ) {
    return (
      <div className={styles['timeline-added-in-adage']}>
        <SvgIcon src={strokeValidIcon} alt="" />
        <span>Ce lieu est référencé sur ADAGE</span>
      </div>
    )
  }

  switch (collectiveDmsApplication.state) {
    case DMSApplicationstatus.EN_CONSTRUCTION:
      return (
        <Timeline
          steps={[
            confirmationSubmittedStep,
            disabledInstructionStep,
            disabledDoneStep,
            disabledAcceptedAdageStep,
          ]}
        />
      )
    case DMSApplicationstatus.EN_INSTRUCTION:
      return (
        <Timeline
          steps={[
            successSubmittedStep,
            waitingInstructionStep,
            disabledDoneStep,
            disabledAcceptedAdageStep,
          ]}
        />
      )
    case DMSApplicationstatus.ACCEPTE:
      if (!hasAdageId) {
        return (
          <Timeline
            steps={[
              successSubmittedStep,
              successInstructionStep,
              successDoneReferencement,
              waitingAdageStep,
            ]}
          />
        )
      }
      if (!hasAdageIdForMoreThan30Days) {
        return (
          <Timeline
            steps={[
              successSubmittedStep,
              successInstructionStep,
              successDoneReferencement,
              successAdageStep,
            ]}
          />
        )
      }

      return (
        <div className={styles['timeline-added-in-adage']}>
          <SvgIcon src={strokeValidIcon} alt="" />
          <span>Ce lieu est référencé sur ADAGE</span>
        </div>
      )
    case DMSApplicationstatus.REFUSE:
      return refusedByDms
    case DMSApplicationstatus.SANS_SUITE:
      return droppedByDms
    /* istanbul ignore next: we dont want to test this case in unit test */
    default:
      throw new Error('Invalid dms status')
  }
}

export default CollectiveDmsTimeline
