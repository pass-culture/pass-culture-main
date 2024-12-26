import { useFormikContext } from 'formik'

import { EacFormat } from 'apiClient/adage'
import { MAX_DETAILS_LENGTH } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { SelectOption } from 'commons/custom_types/form'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { getNationalProgramsForDomains } from '../../constants/getNationalProgramsForDomains'
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

  const eacFormatOptions = Object.entries(EacFormat).map(([, value]) => ({
    value: value,
    label: String(value),
  }))

  const nationalProgramsForDomains = nationalPrograms.filter((program) =>
    getNationalProgramsForDomains(values.domains).includes(program.value)
  )

  return (
    <FormLayout.Section
      description=""
      title="Quel est le type de votre offre ?"
    >
      {domainsOptions.length > 0 && (
        <FormLayout.Row>
          <SelectAutocomplete
            multi
            label="Domaine artistique et culturel"
            name="domains"
            options={domainsOptions}
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
            isOptional
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Section title="Dites-nous en plus sur votre offre culturelle">
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
            <InfoBox>
              Vous pouvez modifier la mise en forme de votre texte.
              <br />
              Utilisez des doubles astérisques pour mettre en{' '}
              <strong>gras</strong> : **exemple** et des tirets bas pour l’
              <em>italique</em> : _exemple_
              <br />
              Vous pourrez vérifier l’affichage à l’étape "Aperçu".
            </InfoBox>
          }
        >
          <TextArea
            label={DESCRIPTION_LABEL}
            maxLength={MAX_DETAILS_LENGTH}
            name="description"
            description="Détaillez ici votre projet et son interêt pédagogique."
            disabled={disableForm}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            isOptional
            label={DURATION_LABEL}
            name="duration"
            description="Format : HH:MM"
            disabled={disableForm}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </FormLayout.Section>
  )
}
