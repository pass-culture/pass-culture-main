import { useFormikContext } from 'formik'

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
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { getNationalProgramsForDomains } from '../../constants/getNationalProgramsForDomains'
import styles from '../OfferEducationalForm.module.scss'

export interface FormTypeProps {
  domainsOptions: SelectOption[]
  nationalPrograms: SelectOption<number>[]
  disableForm: boolean
  isTemplate: boolean
}

export const FormOfferType = ({
  domainsOptions,
  nationalPrograms,
  disableForm,
  isTemplate,
}: FormTypeProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalFormValues>()
  const { logEvent } = useAnalytics()

  const eacFormatOptions = Object.entries(EacFormat).map(([, value]) => ({
    value: value,
    label: String(value),
  }))

  const nationalProgramsForDomains = nationalPrograms.filter((program) =>
    getNationalProgramsForDomains(values.domains).includes(program.value)
  )

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
            <SelectAutocomplete
              multi
              label="Ajoutez un ou plusieurs domaines artistiques"
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
            label="Ajoutez un ou plusieurs formats"
            name="formats"
            disabled={disableForm}
          />
        </FormLayout.Row>

        {nationalPrograms.length > 0 && (
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
                ...nationalProgramsForDomains,
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
              <InfoBox>
                Vous pouvez modifier la mise en forme de votre texte.
                <br />
                Utilisez des doubles astérisques pour mettre en{' '}
                <strong>gras</strong> : **exemple** et des tirets bas pour l’
                <em>italique</em> : _exemple_
                <br />
                Vous pourrez vérifier l’affichage à l’étape "Aperçu".
              </InfoBox>
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
          <TimePicker
            classNameInput={styles['duration-input']}
            isOptional
            label="Indiquez la durée de l’évènement"
            name="duration"
            disabled={disableForm}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
