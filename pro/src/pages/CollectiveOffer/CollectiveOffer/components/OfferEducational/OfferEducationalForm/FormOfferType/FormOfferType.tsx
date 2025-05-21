import { useFormikContext } from 'formik'
import { useState } from 'react'

import { EacFormat } from 'apiClient/adage'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  MAX_DESCRIPTION_LENGTH,
  MAX_PRICE_DETAILS_LENGTH,
  modelTemplate,
} from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { SelectOption } from 'commons/custom_types/form'
import { useFunctionOnce } from 'commons/hooks/useFunctionOnce'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MarkdownInfoBox } from 'components/MarkdownInfoBox/MarkdownInfoBox'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'

import { DomainOption } from '../../useOfferEducationalFormData'
import styles from '../OfferEducationalForm.module.scss'

export interface FormTypeProps {
  domainsOptions: DomainOption[]
  disableForm: boolean
  isTemplate: boolean
}

export const FormOfferType = ({
  domainsOptions,
  disableForm,
  isTemplate,
}: FormTypeProps): JSX.Element => {
  const { values, setFieldValue, setFieldTouched, touched, errors } =
    useFormikContext<OfferEducationalFormValues>()
  const { logEvent } = useAnalytics()

  const getAssociatedPrograms = (selectedDomainIds: string[]) => {
    const selectedDomains = domainsOptions.filter((domain) =>
      selectedDomainIds.includes(domain.id)
    )

    return selectedDomains
      .flatMap((domain) => domain.nationalPrograms)
      .map((program) => ({
        value: program.id,
        label: program.name,
      }))
      .filter(
        (program, index, self) =>
          index === self.findIndex((p) => p.value === program.value)
      )
  }

  const [programsOptions, setProgramsOptions] = useState<SelectOption[]>(() =>
    values.domains.length
      ? getAssociatedPrograms(values.domains.map(String))
      : []
  )

  const eacFormatOptions = Object.entries(EacFormat).map(([, value]) => ({
    id: value,
    label: String(value),
  }))

  const domains: Option[] = domainsOptions.map((domain) => ({
    id: domain.id,
    label: domain.label,
  }))

  const logHasClickedGenerateTemplateDescription = useFunctionOnce(() => {
    logEvent(Events.CLICKED_GENERATE_TEMPLATE_DESCRIPTION, {
      venueId: values.venueId,
      offererId: values.offererId,
      ...(values.domains.length > 0 && {
        domainIds: values.domains.map((id) => Number(id)),
      }),
    })
  })

  const logHasClickedSeeTemplateOfferExample = () => {
    logEvent(Events.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE, {
      venueId: values.venueId,
      offererId: values.offererId,
      ...(values.domains.length > 0 && {
        domainIds: values.domains.map((id) => Number(id)),
      }),
    })
  }

  return (
    <>
      <FormLayout.Section
        description=""
        title="Quel est le type de votre offre ?"
      >
        {domainsOptions.length > 0 && (
          <FormLayout.Row>
            <MultiSelect
              label="Ajoutez un ou plusieurs domaines artistiques"
              name="domains"
              hasSearch
              searchLabel="Recherche"
              options={domains}
              defaultOptions={domains.filter((option) =>
                values.domains.includes(option.id)
              )}
              buttonLabel="Domaines artistiques"
              onSelectedOptionsChanged={async (selectedOptions) => {
                const newDomainIds = selectedOptions.map((option) => option.id)

                await setFieldValue('domains', newDomainIds.map(Number))
                await setFieldTouched('domains', true)

                const newAssociatedPrograms =
                  getAssociatedPrograms(newDomainIds)

                const currentSelectedProgramId = values.nationalProgramId
                const selectedProgramStillExists = newAssociatedPrograms.some(
                  (program) =>
                    program.value.toString() === currentSelectedProgramId
                )

                if (!selectedProgramStillExists && currentSelectedProgramId) {
                  await setFieldValue('nationalProgramId', '')
                }

                setProgramsOptions(newAssociatedPrograms)
              }}
              onBlur={() => setFieldTouched('domains', true)}
              disabled={disableForm}
              required={true}
              error={
                touched.domains && errors.domains
                  ? String(errors.domains)
                  : undefined
              }
            />
          </FormLayout.Row>
        )}

        <FormLayout.Row>
          <MultiSelect
            options={eacFormatOptions}
            defaultOptions={eacFormatOptions.filter((option) =>
              values.formats.includes(option.id)
            )}
            label="Ajoutez un ou plusieurs formats"
            buttonLabel="Formats"
            hasSearch
            searchLabel="Recherche"
            name="formats"
            onSelectedOptionsChanged={(selectedOptions) =>
              setFieldValue('formats', [
                ...selectedOptions.map((elm) => elm.id),
              ])
            }
            required={true}
            disabled={disableForm}
            onBlur={() => setFieldTouched('formats', true)}
            error={
              touched.formats && errors.formats
                ? String(errors.formats)
                : undefined
            }
          />
        </FormLayout.Row>

        {programsOptions.length > 0 && (
          <FormLayout.Row
            sideComponent={
              <InfoBox>
                Un dispositif national est un type de programme d’éducation
                artistique et culturelle auquel sont rattachées certaines
                offres. Si c’est le cas de cette offre, merci de le renseigner.
              </InfoBox>
            }
          >
            <Select
              options={[
                {
                  label: 'Sélectionnez un dispositif national',
                  value: '',
                },
                ...programsOptions,
              ]}
              label="Dispositif national"
              name="nationalProgramId"
              isOptional
              disabled={disableForm}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
      <FormLayout.Section title="Dites-nous en plus sur votre offre culturelle">
        <FormLayout.Row>
          <TextInput
            countCharacters
            label="Titre de l’offre"
            maxLength={110}
            name="title"
            disabled={disableForm}
          />
        </FormLayout.Row>
        <FormLayout.Row
          sideComponent={
            <div className={styles['description-info-boxes']}>
              {isTemplate && (
                <InfoBox>
                  Vous avez du mal a rédiger votre offre ?
                  <br />
                  Nous vous proposons des exemples d’offres vitrines réalisées
                  par d’autres acteurs culturels.
                  <br />
                  <ButtonLink
                    isExternal
                    opensInNewTab
                    variant={ButtonVariant.QUATERNARY}
                    to={
                      'https://aide.passculture.app/hc/fr/articles/17467449038876--Acteurs-Culturels-Consulter-des-exemples-d-offres-vitrine'
                    }
                    onClick={logHasClickedSeeTemplateOfferExample}
                  >
                    Voir des exemples d’offres vitrines
                  </ButtonLink>
                </InfoBox>
              )}
              <MarkdownInfoBox />
            </div>
          }
        >
          <TextArea
            label="Décrivez ici votre projet et son interêt pédagogique"
            maxLength={MAX_DESCRIPTION_LENGTH}
            name="description"
            disabled={disableForm}
            hasTemplateButton={isTemplate}
            hasDefaultPlaceholder
            wordingTemplate={modelTemplate}
            onPressTemplateButton={logHasClickedGenerateTemplateDescription}
          />
        </FormLayout.Row>
        {isTemplate && (
          <FormLayout.Row>
            <TextArea
              disabled={disableForm}
              isOptional
              label="Indiquez le tarif de votre offre"
              maxLength={MAX_PRICE_DETAILS_LENGTH}
              name="priceDetail"
              description="Exemple : par élève ou par groupe scolaire, politique tarifaire REP/REP+ et accompagnateurs..."
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row>
          <TextInput
            isOptional
            classNameInput={styles['duration-input']}
            label="Indiquez la durée de l’évènement"
            name="duration"
            description="Format : HH:MM"
            disabled={disableForm}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
