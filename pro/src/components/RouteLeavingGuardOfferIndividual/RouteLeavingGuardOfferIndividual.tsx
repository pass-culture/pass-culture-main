/* istanbul ignore file : tested through OfferIndividual/Informations & Stocks */
import React, { useState } from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import RouteLeavingGuard from 'components/RouteLeavingGuard'
import { BUTTON_ACTION } from 'components/RouteLeavingGuard/RouteLeavingGuard'
import { OFFER_WIZARD_MODE } from 'core/Offers'

export enum ROUTE_LEAVING_GUARD_TYPE {
  DEFAULT = 'DEFAULT',
  CAN_CREATE_DRAFT = 'CAN_CREATE_DRAFT',
  DRAFT = 'DRAFT',
  EDITION = 'EDITION',
  INTERNAL_VALID = 'INTERNAL_VALID',
  INTERNAL_NOT_VALID = 'INTERNAL_NOT_VALID',
}

export const computeType = (
  mode: OFFER_WIZARD_MODE,
  isFormValid: boolean,
  hasOfferBeenCreated: boolean,
  isInsideOfferJourney: boolean
): ROUTE_LEAVING_GUARD_TYPE => {
  if (
    mode === OFFER_WIZARD_MODE.EDITION &&
    isFormValid &&
    !isInsideOfferJourney
  ) {
    return ROUTE_LEAVING_GUARD_TYPE.EDITION
  } else if (isInsideOfferJourney && isFormValid) {
    return ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID
  } else if (
    mode === OFFER_WIZARD_MODE.CREATION &&
    isFormValid &&
    !hasOfferBeenCreated
  ) {
    return ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT
  } else if (isInsideOfferJourney) {
    return ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID
  } else if (isFormValid) {
    return ROUTE_LEAVING_GUARD_TYPE.DRAFT
  }
  return ROUTE_LEAVING_GUARD_TYPE.DEFAULT
}

export interface IRouteLeavingGuardOfferIndividual {
  mode: OFFER_WIZARD_MODE
  saveForm: () => void
  isFormValid: boolean
  setIsSubmittingFromRouteLeavingGuard: (p: boolean) => void
  tracking?: (p: string) => void
  hasOfferBeenCreated: boolean
}

const RouteLeavingGuardOfferIndividual = ({
  mode,
  saveForm,
  isFormValid,
  setIsSubmittingFromRouteLeavingGuard,
  tracking,
  hasOfferBeenCreated,
}: IRouteLeavingGuardOfferIndividual): JSX.Element => {
  const [nextLocation, setNextLocation] = useState<string>('')

  const routeLeavingGuardTypes = {
    // form dirty and mandatory fields not ok
    [ROUTE_LEAVING_GUARD_TYPE.DEFAULT]: {
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
        text: 'Enregistrer un brouillon et quitter',
        action: () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return saveForm()
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
        action: () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return saveForm()
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
        action: () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return saveForm()
        },
      },
    },
    // internal navigation, form dirty & valid
    [ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID]: {
      dialogTitle: 'Souhaitez-vous enregistrer vos modifications ?',
      description: undefined,
      leftButton: {
        text: 'Quitter sans enregistrer',
        actionType: BUTTON_ACTION.QUIT_WITHOUT_SAVING,
      },
      rightButton: {
        text: 'Enregistrer les modifications',
        action: () => {
          setIsSubmittingFromRouteLeavingGuard(true)
          return saveForm()
        },
      },
    },
    // internal navigation, form dirty & not valid
    [ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID]: {
      dialogTitle: 'Si vous changez de page vos informations seront perdues',
      description:
        'Votre offre ne sera pas sauvegardée et toutes les informations seront perdues.',
      leftButton: {
        text: 'Annuler',
      },
      rightButton: {
        text: 'Quitter la page',
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
      when
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
