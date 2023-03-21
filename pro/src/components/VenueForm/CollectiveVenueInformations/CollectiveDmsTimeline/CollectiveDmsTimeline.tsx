import React from 'react'

import { ExternalLinkIcon } from 'icons'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Timeline, { TimelineStepType } from 'ui-kit/Timeline/Timeline'

import styles from './CollectiveDmsTimeline.module.scss'

const CollectiveDmsTimeline = () => {
  //const collectiveDmsStatus = venue.collectiveDmsStatus // FIX ME : collectiveDmsStatus is not yet a property of IVenue
  const collectiveDmsStatus = 'DRAFT'
  // const collectiveDmsApplicationLink = link to venue.collectiveDmsApplicationId // FIX ME : collectiveDmsApplicationId is not yet a property of IVenue
  const collectiveDmsApplicationLink = 'todo'
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
  const disabledAcceptedAdageStep = {
    type: TimelineStepType.DISABLED,
    content: (
      <div className={styles['timeline-step-title-disabled']}>
        Votre lieu a été ajouté dans ADAGE
      </div>
    ),
  }

  switch (collectiveDmsStatus) {
    case 'DRAFT':
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
    // istanbul ignore next: FIX ME not implemented yet
    default:
      throw new Error('Invalid dms status')
  }
}

export default CollectiveDmsTimeline
