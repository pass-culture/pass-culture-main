import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLeftIcon from '@/icons/full-left.svg'

interface ActionBarLeftProps {
  isDisabled: boolean
  isEvent: boolean
  mode: OFFER_WIZARD_MODE
  onClickNext?: () => void
  onClickPrevious?: () => void
  publicationMode?: 'later' | 'now'
  saveEditionChangesButtonRef?: React.RefObject<HTMLButtonElement | null>
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
}

export const ActionBarLeft = ({
  isDisabled,
  isEvent,
  mode,
  onClickNext,
  onClickPrevious,
  saveEditionChangesButtonRef,
  step,
}: Readonly<ActionBarLeftProps>) => {
  if (mode === OFFER_WIZARD_MODE.CREATION) {
    return (
      <Button
        icon={fullLeftIcon}
        onClick={onClickPrevious}
        variant={ButtonVariant.SECONDARY}
        disabled={isDisabled}
        label="Retour"
      />
    )
  }

  if (
    mode === OFFER_WIZARD_MODE.EDITION &&
    step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE &&
    isEvent
  ) {
    return (
      <Button
        onClick={onClickPrevious}
        variant={ButtonVariant.SECONDARY}
        label="Quitter le mode édition"
      />
    )
  }

  if (step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY) {
    const backOfferUrl = computeIndividualOffersUrl({})

    return (
      <Button as="a" to={backOfferUrl} label="Retour à la liste des offres" />
    )
  }

  return (
    <>
      <Button
        onClick={onClickPrevious}
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        label="Annuler et quitter"
      />

      <Button
        type="submit"
        onClick={onClickNext}
        disabled={isDisabled}
        ref={saveEditionChangesButtonRef}
        label="Enregistrer les modifications"
      />
    </>
  )
}
