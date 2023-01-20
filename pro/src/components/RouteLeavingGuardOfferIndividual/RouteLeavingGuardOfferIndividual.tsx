/* istanbul ignore file : tested through OfferIndividual/Informations & Stocks */
import React, { useState } from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import RouteLeavingGuard from 'components/RouteLeavingGuard'
import { BUTTON_ACTION } from 'components/RouteLeavingGuard/RouteLeavingGuard'
import { OFFER_WIZARD_MODE } from 'core/Offers'

export enum ROUTE_LEAVING_GUARD_TYPE {
  NOT_VALID_DEFAULT = 'NOT_VALID_DEFAULT',
  CAN_CREATE_DRAFT = 'CAN_CREATE_DRAFT',
  CANNOT_CREATE_DRAFT = 'CANNOT_CREATE_DRAFT',
  DRAFT = 'DRAFT',
  EDITION = 'EDITION',
  INTERNAL_VALID = 'INTERNAL_VALID',
}

export const computeType = (
  mode: OFFER_WIZARD_MODE,
  isFormValid: boolean,
  hasOfferBeenCreated: boolean,
  isInsideOfferJourney: boolean
): ROUTE_LEAVING_GUARD_TYPE => {
  if (isFormValid) {
    if (isInsideOfferJourney) {
      return ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID
    }
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      return ROUTE_LEAVING_GUARD_TYPE.EDITION
    } else if (mode === OFFER_WIZARD_MODE.DRAFT) {
      return ROUTE_LEAVING_GUARD_TYPE.DRAFT
    } else if (mode === OFFER_WIZARD_MODE.CREATION && !hasOfferBeenCreated) {
      return ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT
    } else if (mode === OFFER_WIZARD_MODE.CREATION && hasOfferBeenCreated) {
      return ROUTE_LEAVING_GUARD_TYPE.DRAFT
    }
  } else if (
    mode === OFFER_WIZARD_MODE.CREATION &&
    !isFormValid &&
    !hasOfferBeenCreated &&
    !isInsideOfferJourney
  ) {
    return ROUTE_LEAVING_GUARD_TYPE.CANNOT_CREATE_DRAFT
  }

  return ROUTE_LEAVING_GUARD_TYPE.NOT_VALID_DEFAULT
}

export interface IRouteLeavingGuardOfferIndividual {
  mode: OFFER_WIZARD_MODE
  saveForm: () => Promise<void>
  isFormValid: boolean
  setIsSubmittingFromRouteLeavingGuard: (p: boolean) => void
  tracking?: (p: string) => void
  hasOfferBeenCreated: boolean
  when: boolean
}

const RouteLeavingGuardOfferIndividual = ({
  mode,
  saveForm,
  isFormValid,
  setIsSubmittingFromRouteLeavingGuard,
  tracking,
  hasOfferBeenCreated,
  when,
}: IRouteLeavingGuardOfferIndividual): JSX.Element => {
  const [nextLocation, setNextLocation] = useState<string>('')

  const routeLeavingGuardTypes = {
    // mode creation + form dirty and mandatory fields not ok
    [ROUTE_LEAVING_GUARD_TYPE.CANNOT_CREATE_DRAFT]: {
      dialogTitle: 'Souhaitez-vous quitter la création d’offre ?',
      description:
        'Votre offre ne sera pas sauvegardée et toutes les informations seront perdues.',
      leftButton: {
        text: 'Annuler',
      },
      rightButton: {
        text: 'Quitter',
      },
    },
    // mode creation + mandatory fields ok + offer did not exist
    [ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT]: {
      dialogTitle:
        'Souhaitez-vous enregistrer cette offre en brouillon avant de quitter ?',
      description:
        'Vous pourrez la retrouver dans la liste de vos offres pour la compléter et la publier plus tard.',
      leftButton: {
        text: 'Quitter sans enregistrer',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Sauvegarder le brouillon et quitter',
        action: async () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return await saveForm()
        },
      },
    },
    // mode draft or creation, form dirty & valid + offer did exist
    [ROUTE_LEAVING_GUARD_TYPE.DRAFT]: {
      dialogTitle:
        'Souhaitez-vous enregistrer vos modifications avant de quitter ?',
      description:
        'Si vous quittez, les informations saisies ne seront pas sauvegardées dans votre brouillon.',
      leftButton: {
        text: 'Quitter sans enregistrer',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Enregistrer les modifications',
        action: async () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return await saveForm()
        },
      },
    },
    // mode edition, form dirty & valid
    [ROUTE_LEAVING_GUARD_TYPE.EDITION]: {
      dialogTitle:
        'Souhaitez-vous enregistrer vos modifications avant de quitter ?',
      description:
        'Si vous quittez, les informations saisies ne seront pas sauvegardées.',
      leftButton: {
        text: 'Quitter sans enregistrer',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Enregistrer les modifications',
        action: async () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return await saveForm()
        },
      },
    },
    // internal navigation, form dirty & valid
    [ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID]: {
      dialogTitle: 'Souhaitez-vous enregistrer vos modifications ?',
      description: undefined,
      leftButton: {
        text: 'Ne pas enregistrer',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Enregistrer les modifications',
        action: async () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return await saveForm()
        },
      },
    },
    // form dirty & not valid
    [ROUTE_LEAVING_GUARD_TYPE.NOT_VALID_DEFAULT]: {
      dialogTitle: 'Des erreurs sont présentes sur cette page',
      description:
        'En poursuivant la navigation, vos modifications ne seront pas sauvegardées.',
      leftButton: {
        text: 'Poursuivre la navigation',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Rester sur cette page',
        actionType: BUTTON_ACTION.CANCEL,
      },
    },
  }

  const isInsideOfferJourney = Object.values(OFFER_WIZARD_STEP_IDS).some(
    (step: string) => {
      if (nextLocation.includes(step)) {
        return true
      }
      return false
    }
  )
  const type = computeType(
    mode,
    isFormValid,
    hasOfferBeenCreated,
    isInsideOfferJourney
  )

  const shouldBlockNavigation = (chosenLocation: Location) => {
    setNextLocation(chosenLocation.pathname)
    return {
      shouldBlock: true,
      redirectPath: chosenLocation.pathname,
    }
  }

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
      dialogTitle={routeLeavingGuardTypes[type].dialogTitle}
      leftButton={routeLeavingGuardTypes[type].leftButton}
      rightButton={routeLeavingGuardTypes[type].rightButton}
      tracking={tracking}
    >
      {routeLeavingGuardTypes[type].description && (
        <p>{routeLeavingGuardTypes[type].description}</p>
      )}
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferIndividual
