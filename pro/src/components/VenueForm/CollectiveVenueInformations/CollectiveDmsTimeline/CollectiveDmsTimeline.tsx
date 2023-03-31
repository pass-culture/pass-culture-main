import React from 'react'

import { DMSApplicationForEAC } from 'apiClient/v1'
import { ExternalLinkIcon, PenIcon } from 'icons'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Timeline, { TimelineStepType } from 'ui-kit/Timeline/Timeline'

import styles from './CollectiveDmsTimeline.module.scss'

// Modify status value with backend status value when it's ready
export const DMS_STATUS = {
  DRAFT: 'DRAFT',
  SUBMITTED: 'SUBMITTED',
  INSTRUCTION: 'INSTRUCTION',
  ADD_IN_ADAGE: 'ADD_IN_ADAGE',
  ADDED_IN_ADAGE: 'ADDED_IN_ADAGE',
}

const CollectiveDmsTimeline = ({
  collectiveDmsApplication,
}: {
  collectiveDmsApplication: DMSApplicationForEAC | null
}) => {
  // const collectiveDmsApplicationLink = link to venue.collectiveDmsApplicationId // FIX ME : collectiveDmsApplicationId is not yet a property of IVenue
  const collectiveDmsApplicationLink = DMS_STATUS.ADDED_IN_ADAGE
  const waitingDraftStep = {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <div className={styles['timeline-step-title']}>
          Déposez votre demande de référencement
        </div>
        <div className={styles['timeline-infobox']}>
          <div className={styles['timeline-infobox-text']}>
            Votre dossier est au statut “brouillon”. Vous devez le publier si
            vous souhaitez qu’il soit traité.
          </div>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            link={{
              to: collectiveDmsApplicationLink,
              isExternal: true,
            }}
            Icon={ExternalLinkIcon}
          >
            Modifier mon dossier sur Démarches Simplifiées
          </ButtonLink>
        </div>
      </>
    ),
  }

  const successSubmittedStep = {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        <div className={styles['timeline-step-title-disabled']}>
          Votre dossier a été déposé
        </div>
        <div>28 mars 2023</div>
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
          28 mars 2023
          <br />
          Votre demande de référencement a bien été déposée. Elle sera étudiée
          par les services du Ministère de l’Education Nationale et de la
          Culture lors d’une commission mensuelle. En fonction du nombre de
          dossiers en cours, cela peut prendre jusqu’à 3 mois.
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={ExternalLinkIcon}
        >
          Modifier mon dossier sur Démarches Simplifiées
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
          28 février 2023
          <br />
          Votre dossier est en cours d’instruction par la commission régionale
          DAAC et DRAC où est déclaré votre siège social. Si votre dossier
          concerne un établissement public, il est traité par le Ministère de la
          Culture.
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={ExternalLinkIcon}
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
        <div>28 février 2023</div>
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
          28 février 2023
          <br />
          Votre lieu sera bientôt ajouté dans ADAGE par le Ministère de
          l’Éducation Nationale. Cela peut prendre quelques jours.
        </div>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: collectiveDmsApplicationLink,
            isExternal: true,
          }}
          Icon={ExternalLinkIcon}
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
        <div>
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
        <div>5 mars 2023</div>
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
              to: collectiveDmsApplicationLink,
              isExternal: true,
            }}
            Icon={PenIcon}
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

  switch (collectiveDmsApplication?.state) {
    case DMS_STATUS.DRAFT:
      return (
        <Timeline
          steps={[
            waitingDraftStep,
            disabledInstructionStep,
            disabledDoneStep,
            disabledAcceptedAdageStep,
          ]}
        />
      )
    case DMS_STATUS.SUBMITTED:
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
    case DMS_STATUS.INSTRUCTION:
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
    case DMS_STATUS.ADD_IN_ADAGE:
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
    case DMS_STATUS.ADDED_IN_ADAGE:
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
    default:
      throw new Error('Invalid dms status')
  }
}

export default CollectiveDmsTimeline
