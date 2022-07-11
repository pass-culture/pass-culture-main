import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import React from 'react'
import { SubmitButton } from 'ui-kit'
import useActiveFeature from 'components/hooks/useActiveFeature'

interface IFormActionsProps {
  cancelUrl?: string
  canSubmit: boolean
  isDraft: boolean
  isSubmiting: boolean
  onSubmit: () => void
}

const FormActions = ({
  isDraft,
  cancelUrl,
  canSubmit,
  isSubmiting,
  onSubmit,
}: IFormActionsProps): JSX.Element => {
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

  return (
    <>
      {cancelUrl && (
        <ButtonLink variant={ButtonVariant.SECONDARY} to={cancelUrl}>
          {isDraft
            ? 'Étape précédente'
            : useSummaryPage
            ? `Voir le détail de l'offre`
            : 'Annuler et quitter'}
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
          : 'Enregistrer'}
      </SubmitButton>
    </>
  )
}

export default FormActions
