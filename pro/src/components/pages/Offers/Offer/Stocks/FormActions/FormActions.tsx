import React from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
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
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

  return (
    <>
      {cancelUrl && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          to={cancelUrl}
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
        {isDraft
          ? useSummaryPage
            ? 'Étape suivante'
            : 'Valider et créer l’offre'
          : 'Enregistrer les modifications'}
      </SubmitButton>
    </>
  )
}

export default FormActions
