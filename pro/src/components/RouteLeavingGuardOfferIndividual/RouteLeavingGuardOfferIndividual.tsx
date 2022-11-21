/* istanbul ignore file : tested through OfferIndividual/Informations & Stocks */
import React from 'react'

import RouteLeavingGuard from 'components/RouteLeavingGuard'
import { BUTTON_ACTION } from 'components/RouteLeavingGuard/RouteLeavingGuard'
import { OFFER_WIZARD_MODE } from 'core/Offers'

export enum ROUTE_LEAVING_GUARD_TYPE {
  DEFAULT = 'DEFAULT',
  CAN_CREATE_DRAFT = 'CAN_CREATE_DRAFT',
  DRAFT = 'DRAFT',
  EDITION = 'EDITION',
}

const computeType = (
  mode: OFFER_WIZARD_MODE,
  isFormValid: boolean,
  hasOfferBeenCreated: boolean
): ROUTE_LEAVING_GUARD_TYPE => {
  if (mode === OFFER_WIZARD_MODE.EDITION && isFormValid) {
    return ROUTE_LEAVING_GUARD_TYPE.EDITION
  } else if (mode === OFFER_WIZARD_MODE.DRAFT && isFormValid) {
    return ROUTE_LEAVING_GUARD_TYPE.DRAFT
  } else if (
    mode === OFFER_WIZARD_MODE.CREATION &&
    !hasOfferBeenCreated &&
    isFormValid
  ) {
    return ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT
  }
  return ROUTE_LEAVING_GUARD_TYPE.DEFAULT
}

export interface IRouteLeavingGuardOfferIndividual {
  mode: OFFER_WIZARD_MODE
  saveForm: () => void
  hasOfferBeenCreated: boolean
  isFormValid: boolean
  setIsSubmittingFromRouteLeavingGuard: (p: boolean) => void
}

const RouteLeavingGuardOfferIndividual = ({
  mode,
  saveForm,
  hasOfferBeenCreated,
  isFormValid,
  setIsSubmittingFromRouteLeavingGuard,
}: IRouteLeavingGuardOfferIndividual): JSX.Element => {
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
    // mode creation + mandatory fields ok
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
    // mode draft, form dirty
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
    // mode edition, form dirty
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
  }

  const type = computeType(mode, isFormValid, hasOfferBeenCreated)

  const shouldBlockNavigation = (location: Location) => ({
    shouldBlock: true,
    redirectPath: location.pathname,
  })

  return (
    <RouteLeavingGuard
      shouldBlockNavigation={shouldBlockNavigation}
      when
      dialogTitle={routeLeavingGuardTypes[type].dialogTitle}
      leftButton={routeLeavingGuardTypes[type].leftButton}
      rightButton={routeLeavingGuardTypes[type].rightButton}
    >
      <p>{routeLeavingGuardTypes[type].description}</p>
    </RouteLeavingGuard>
  )
}

export default RouteLeavingGuardOfferIndividual
