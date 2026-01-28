import cn from 'classnames'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Mode } from '@/commons/core/OfferEducational/types'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullHideIcon from '@/icons/full-hide.svg'
import strokeCheckIcon from '@/icons/stroke-check.svg'

import style from './OfferEducationalActions.module.scss'

export interface OfferEducationalActionsProps {
  className?: string
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  mode?: Mode
}

export const OfferEducationalActions = ({
  className,
  offer,
  mode,
}: OfferEducationalActionsProps): JSX.Element => {
  const snackBar = useSnackBar()

  const { mutate } = useSWRConfig()

  const setIsOfferActive = async (isActive: boolean) => {
    try {
      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: [offer.id],
        isActive,
      })
      snackBar.success(
        isActive
          ? 'Votre offre est maintenant active et visible dans ADAGE'
          : 'Votre offre est mise en pause et n’est plus visible sur ADAGE'
      )
    } catch (error) {
      if (error instanceof Error) {
        return snackBar.error(
          `Une erreur est survenue lors de ${
            isActive ? 'l’activation' : 'la désactivation'
          } de votre offre. ${error.message}`
        )
      } else {
        snackBar.error(
          `Une  erreur est survenue lors de ${
            isActive ? 'l’activation' : 'la désactivation'
          } de votre offre.`
        )
      }
    }

    await mutate([
      offer.isTemplate
        ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
        : GET_COLLECTIVE_OFFER_QUERY_KEY,
      offer.id,
    ])
  }

  const shouldShowOfferActions =
    mode === Mode.EDITION || mode === Mode.READ_ONLY

  const canPublishOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
  )

  const canHideOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_HIDE
  )

  return (
    <>
      {shouldShowOfferActions && (
        <div className={cn(style['actions'], className)}>
          {canHideOffer && (
            <Button
              icon={fullHideIcon}
              onClick={() => setIsOfferActive(false)}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              label="Mettre en pause"
            />
          )}
          {canPublishOffer && (
            <Button
              icon={strokeCheckIcon}
              onClick={() => setIsOfferActive(true)}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              label="Publier"
            />
          )}
          <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
        </div>
      )}
    </>
  )
}
