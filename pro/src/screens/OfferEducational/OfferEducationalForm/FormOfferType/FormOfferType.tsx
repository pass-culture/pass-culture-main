import { useFormikContext } from 'formik'

import { EacFormat } from 'apiClient/adage'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MAX_DETAILS_LENGTH } from 'core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { SelectOption } from 'custom_types/form'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { getNationalProgramsForDomains } from 'screens/OfferEducational/constants/getNationalProgramsForDomains'
import { MultiSelectAutocomplete } from 'ui-kit/form/MultiSelectAutoComplete/MultiSelectAutocomplete'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import {
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'

export interface FormTypeProps {
  domainsOptions: SelectOption[]
  nationalPrograms: SelectOption<number>[]
  disableForm: boolean
}

export const FormOfferType = ({
  domainsOptions,
  nationalPrograms,
  disableForm,
}: FormTypeProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalFormValues>()
  const isMarkdownDescriptionEnabled = useActiveFeature(
    'WIP_ENABLE_OFFER_MARKDOWN_DESCRIPTION'
  )

  const eacFormatOptions = Object.entries(EacFormat).map(([, value]) => ({
    value: value,
    label: String(value),
  }))

  const nationalProgramsForDomains = nationalPrograms.filter((program) =>
    getNationalProgramsForDomains(values.domains).includes(program.value)
  )

  return (
    <FormLayout.Section
      description="Le type de l’offre permet de la caractériser et de la valoriser au mieux pour les enseignants et chefs d’établissement."
      title="Type d’offre"
    >
      {domainsOptions.length > 0 && (
        <FormLayout.Row>
          <MultiSelectAutocomplete
            options={domainsOptions}
            pluralLabel="Domaines artistiques et culturels"
            label="Domaine artistique et culturel"
            name="domains"
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        <SelectAutocomplete
          multi
          options={eacFormatOptions}
          label="Format"
          placeholder="Sélectionner un format"
          name="formats"
          disabled={disableForm}
        />
      </FormLayout.Row>

      {nationalPrograms.length > 0 && (
        <FormLayout.Row
          sideComponent={
            <InfoBox>
              Un dispositif national est un type de programme d’éducation
              artistique et culturelle auquel sont rattachées certaines offres.
              Si c’est le cas de cette offre, merci de le renseigner.
            </InfoBox>
          }
        >
          <Select
            options={[
              {
                label: 'Sélectionnez un dispositif national',
                value: '',
              },
              ...nationalProgramsForDomains,
            ]}
            label="Dispositif national"
            name="nationalProgramId"
            placeholder="Séléctionner un dispositif national"
            isOptional
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Section title="Informations artistiques">
        <FormLayout.Row>
          <TextInput
            countCharacters
            label={TITLE_LABEL}
            maxLength={110}
            name="title"
            disabled={disableForm}
          />
        </FormLayout.Row>
        <FormLayout.Row
          sideComponent={
            isMarkdownDescriptionEnabled ? (
              <InfoBox>
                Vous pouvez modifier la mise en forme de votre texte.
                <br />
                Utilisez des doubles astérisques pour mettre en{' '}
                <strong>gras</strong> : **exemple** et des tirets bas pour l’
                <em>italique</em> : _exemple_
                <br />
                Vous pourrez vérifier l’affichage à l’étape "Aperçu".
              </InfoBox>
            ) : null
          }
        >
          <TextArea
            countCharacters
            label={DESCRIPTION_LABEL}
            maxLength={MAX_DETAILS_LENGTH}
            name="description"
            placeholder="Détaillez ici votre projet et son interêt pédagogique."
            disabled={disableForm}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            isOptional
            label={DURATION_LABEL}
            name="duration"
            placeholder="HH:MM"
            disabled={disableForm}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </FormLayout.Section>
  )
}
