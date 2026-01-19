import { useFormContext } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLeftIcon from '@/icons/full-left.svg'
import { ActionBarDraftStatus } from '@/pages/IndividualOffer/components/ActionBar/ActionBarDraftStatus/ActionBarDraftStatus'

export type TimetableOpeningHoursActionsBarProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
}

export function TimetableOpeningHoursActionsBar({
  offer,
  mode,
}: TimetableOpeningHoursActionsBarProps) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const form = useFormContext()

  function handlePreviousStep() {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
      return
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
        isOnboarding,
      })
    )
  }

  return (
    <ActionsBarSticky hasSideNav={!isOnboarding}>
      <ActionsBarSticky.Left>
        {
          <Button
            type="button"
            variant={ButtonVariant.SECONDARY}
            onClick={handlePreviousStep}
            icon={fullLeftIcon}
            label={
              mode === OFFER_WIZARD_MODE.READ_ONLY
                ? 'Retour à la liste des offres'
                : mode === OFFER_WIZARD_MODE.EDITION
                  ? 'Annuler et quitter'
                  : 'Retour'
            }
          />
        }
      </ActionsBarSticky.Left>
      {mode !== OFFER_WIZARD_MODE.READ_ONLY && (
        <ActionsBarSticky.Right>
          {form.formState.isDirty !== undefined && (
            <ActionBarDraftStatus isSaved={form.formState.isDirty === false} />
          )}
          <Button
            type="submit"
            label={
              mode === OFFER_WIZARD_MODE.EDITION
                ? 'Enregistrer les modifications'
                : 'Enregistrer et continuer'
            }
          />
        </ActionsBarSticky.Right>
      )}
    </ActionsBarSticky>
  )
}
