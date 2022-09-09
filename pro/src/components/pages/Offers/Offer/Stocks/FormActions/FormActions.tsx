import React from 'react'

import { SubmitButton } from 'ui-kit'
import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IFormActionsProps {
  cancelUrl?: string
  canSubmit: boolean
  isDraft: boolean
  isSubmiting: boolean
  onSubmit: () => void
  onCancelClick?: () => void
}

const FormActions = ({
  isDraft,
  cancelUrl,
  canSubmit,
  isSubmiting,
  onSubmit,
  onCancelClick,
}: IFormActionsProps): JSX.Element => {
  return (
    <>
      {cancelUrl && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{ to: cancelUrl, isExternal: false }}
          onClick={onCancelClick ? onCancelClick : undefined}
        >
          {isDraft ? 'Étape précédente' : 'Annuler et quitter'}
        </ButtonLink>
      )}

      <SubmitButton
        disabled={!canSubmit}
        isLoading={isSubmiting}
        onClick={onSubmit}
      >
        {isDraft ? 'Étape suivante' : 'Enregistrer les modifications'}
      </SubmitButton>
    </>
  )
}

export default FormActions
