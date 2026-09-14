import { useAnalytics } from '@/app/App/analytics/firebase'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLeftIcon from '@/icons/full-left.svg'

interface ActionBarLeftProps {
  isDisabled: boolean
  mode: OFFER_WIZARD_MODE
  onClickNext?: () => void
  onClickPrevious?: () => void
  publicationMode?: 'later' | 'now'
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
}

export const ActionBarLeft = ({
  isDisabled,
  mode,
  onClickNext,
  onClickPrevious,
  step,
}: Readonly<ActionBarLeftProps>) => {
  const { logEvent } = useAnalytics()
  const { offerId } = useIndividualOfferContext()

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

  if (step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY) {
    const backOfferUrl = computeIndividualOffersUrl({})

    return (
      <Button
        as="router-link"
        to={backOfferUrl}
        label="Retour à la liste des offres"
      />
    )
  }

  return (
    <Button
      type="submit"
      onClick={() => {
        logEvent(Events.CLICKED_INDIVIDUAL_OFFER_MODIFICATION, {
          offerId: offerId ?? undefined,
        })
        onClickNext?.()
      }}
      disabled={isDisabled}
      label="Enregistrer les modifications"
    />
  )
}
