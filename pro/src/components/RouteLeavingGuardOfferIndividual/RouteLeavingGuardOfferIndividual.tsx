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
    // mode creation + mandatory fields not ok, form dirty
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

  const type =
    mode === OFFER_WIZARD_MODE.EDITION && isFormValid
      ? ROUTE_LEAVING_GUARD_TYPE.EDITION
      : mode === OFFER_WIZARD_MODE.DRAFT && isFormValid
      ? ROUTE_LEAVING_GUARD_TYPE.DRAFT
      : mode === OFFER_WIZARD_MODE.CREATION &&
        !hasOfferBeenCreated &&
        isFormValid
      ? ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT
      : ROUTE_LEAVING_GUARD_TYPE.DEFAULT

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
