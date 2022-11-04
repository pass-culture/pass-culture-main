import cn from 'classnames'
import React from 'react'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'custom_types/offer'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { Button, ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './OfferFormActions.module.scss'

interface IOfferFormActionsProps {
  canSaveDraft: boolean
  cancelUrl: string
  onClickNext: () => void
  onClickSaveDraft: () => void
  isDisabled: boolean
  isSubmitLoading: boolean
  isEdition: boolean
  offer?: Offer
}

const OfferFormActions = ({
  canSaveDraft,
  isDisabled,
  isSubmitLoading,
  isEdition,
  cancelUrl,
  onClickNext,
  onClickSaveDraft,
  offer,
}: IOfferFormActionsProps) => {
  const { logEvent } = useAnalytics()
  const isDraftEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')
  const onCancelClick = () => {
    if (isEdition)
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OfferBreadcrumbStep.DETAILS,
        to: OfferBreadcrumbStep.SUMMARY,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: true,
        isDraft: offer?.status === OFFER_STATUS_DRAFT,
        offerId: offer?.id,
      })
    else
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OfferBreadcrumbStep.DETAILS,
        to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: false,
        isDraft: true,
      })
  }

  return (
    <div className={cn(styles['form-actions'])}>
      <div>
        <ButtonLink
          className={styles['action']}
          link={{
            to: cancelUrl,
            isExternal: false,
          }}
          variant={ButtonVariant.SECONDARY}
          onClick={onCancelClick}
        >
          {'Annuler et quitter'}
        </ButtonLink>
      </div>
      <div className={styles['right-actions']}>
        {canSaveDraft && isDraftEnabled && (
          <Button
            className={styles['action']}
            disabled={isDisabled || isSubmitLoading}
            onClick={onClickSaveDraft}
            variant={ButtonVariant.SECONDARY}
          >
            Sauvegarder le brouillon
          </Button>
        )}
        <SubmitButton
          disabled={isDisabled || isSubmitLoading}
          onClick={onClickNext}
        >
          {isEdition ? 'Enregistrer les modifications' : 'Étape suivante'}
        </SubmitButton>
      </div>
    </div>
  )
}

export default OfferFormActions
