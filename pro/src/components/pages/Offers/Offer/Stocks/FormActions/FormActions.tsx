import React from 'react'

import useActiveFeature from 'hooks/useActiveFeature'
import useIsCompletingDraft from 'new_components/OfferIndividualStepper/hooks/useIsCompletingDraft'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import { SubmitButton } from 'ui-kit'
import { Button, ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IFormActionsProps {
  cancelUrl?: string
  canSubmit: boolean
  isDraft: boolean
  isSubmiting: boolean
  onSubmit: () => void
  onCancelClick: () => void
  onSubmitDraft: () => void
}

const FormActions = ({
  isDraft,
  cancelUrl,
  canSubmit,
  isSubmiting,
  onSubmit,
  onSubmitDraft,
  onCancelClick,
}: IFormActionsProps): JSX.Element => {
  const isCreation = useIsCreation()
  const isCompletingDraft = useIsCompletingDraft()
  const isDraftEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')

  return (
    <>
      {cancelUrl && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{ to: cancelUrl, isExternal: false }}
          onClick={onCancelClick}
        >
          {isDraft ? 'Étape précédente' : 'Annuler et quitter'}
        </ButtonLink>
      )}

      <div>
        {(isCreation || isCompletingDraft) && isDraftEnabled && (
          <Button
            disabled={!canSubmit || isSubmiting}
            onClick={onSubmitDraft}
            variant={ButtonVariant.SECONDARY}
          >
            Sauvegarder le brouillon
          </Button>
        )}

        <SubmitButton disabled={!canSubmit || isSubmiting} onClick={onSubmit}>
          {isDraft ? 'Étape suivante' : 'Enregistrer les modifications'}
        </SubmitButton>
      </div>
    </>
  )
}

export default FormActions
