import { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { EacFormat } from '@/apiClient/adage'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  MAX_DESCRIPTION_LENGTH,
  MAX_PRICE_DETAILS_LENGTH,
  modelTemplate,
} from '@/commons/core/OfferEducational/constants'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { useFunctionOnce } from '@/commons/hooks/useFunctionOnce'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import { MultiSelect, type Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import type { DomainOption } from '../../useOfferEducationalFormData'
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
  const { watch, setValue, getFieldState, register } =
    useFormContext<OfferEducationalFormValues>()

  const domainsValue = watch('domains')
  const venueIdValue = watch('venueId')

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

  const [programsOptions, setProgramsOptions] = useState<
    SelectOption<number>[]
  >(() => (domainsValue?.length ? getAssociatedPrograms(domainsValue) : []))

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
      venueId: venueIdValue,
      offererId: watch('offererId'),
      ...(domainsValue &&
        domainsValue.length > 0 && {
          domainIds: domainsValue.map((id) => Number(id)),
        }),
    })
  })

  const logHasClickedSeeTemplateOfferExample = () => {
    logEvent(Events.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE, {
      venueId: venueIdValue,
      offererId: watch('offererId'),
      ...(domainsValue &&
        domainsValue.length > 0 && {
          domainIds: domainsValue.map((id) => Number(id)),
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
              searchLabel="Rechercher un domaine artistique"
              options={domains}
              defaultOptions={domains.filter((option) =>
                domainsValue?.includes(option.id)
              )}
              buttonLabel="Domaines artistiques"
              onSelectedOptionsChanged={(selectedOptions) => {
                const newDomainIds = selectedOptions.map((option) => option.id)

                setValue('domains', newDomainIds, { shouldValidate: true })

                const newAssociatedPrograms =
                  getAssociatedPrograms(newDomainIds)

                const currentSelectedProgramId = watch('nationalProgramId')
                const selectedProgramStillExists = newAssociatedPrograms.some(
                  (program) =>
                    program.value.toString() === currentSelectedProgramId
                )

                if (!selectedProgramStillExists && currentSelectedProgramId) {
                  setValue('nationalProgramId', '')
                }

                setProgramsOptions(newAssociatedPrograms)
              }}
              disabled={disableForm}
              required={true}
              error={getFieldState('domains').error?.message}
            />
          </FormLayout.Row>
        )}

        <FormLayout.Row>
          <MultiSelect
            options={eacFormatOptions}
            defaultOptions={eacFormatOptions.filter((option) =>
              watch('formats').includes(option.id)
            )}
            label="Ajoutez un ou plusieurs formats"
            buttonLabel="Formats"
            hasSearch
            searchLabel="Rechercher un format"
            name="formats"
            onSelectedOptionsChanged={(selectedOptions) =>
              setValue(
                'formats',
                [...selectedOptions.map((elm) => elm.id)] as EacFormat[],
                { shouldValidate: true }
              )
            }
            required
            disabled={disableForm}
            error={getFieldState('formats').error?.message}
          />
        </FormLayout.Row>

        {programsOptions.length > 0 && (
          <FormLayout.Row
            sideComponent={
              <TipsBanner>
                Un dispositif national est un type de programme d’éducation
                artistique et culturelle auquel sont rattachées certaines
                offres. Si c’est le cas de cette offre, merci de le renseigner.
              </TipsBanner>
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
              {...register('nationalProgramId')}
              error={getFieldState('nationalProgramId').error?.message}
              disabled={disableForm}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
      <FormLayout.Section title="Dites-nous en plus sur votre offre culturelle">
        <FormLayout.Row className={styles['title']}>
          <TextInput
            maxCharactersCount={110}
            required
            label="Titre de l’offre"
            {...register('title')}
            error={getFieldState('title').error?.message}
            disabled={disableForm}
          />
        </FormLayout.Row>
        <FormLayout.Row
          className={styles['description']}
          sideComponent={
            <div className={styles['description-info-boxes']}>
              {isTemplate && (
                <TipsBanner>
                  <span className={styles['description-info-spacing']}>
                    Vous avez du mal a rédiger votre offre ? Nous vous proposons
                    des exemples d’offres vitrines réalisées par d’autres
                    acteurs culturels.
                  </span>
                  <Button
                    as="a"
                    icon={fullLinkIcon}
                    variant={ButtonVariant.TERTIARY}
                    size={ButtonSize.SMALL}
                    label="Voir des exemples d’offres vitrines"
                    onClick={logHasClickedSeeTemplateOfferExample}
                    to="https://aide.passculture.app/hc/fr/articles/17467449038876--Acteurs-Culturels-Consulter-des-exemples-d-offres-vitrine"
                    isExternal
                    opensInNewTab
                  />
                </TipsBanner>
              )}
              <MarkdownInfoBox />
            </div>
          }
        >
          <TextArea
            label="Décrivez ici votre projet et son interêt pédagogique"
            maxLength={MAX_DESCRIPTION_LENGTH}
            {...register('description')}
            error={getFieldState('description').error?.message}
            required
            disabled={disableForm}
            hasTemplateButton={isTemplate}
            hasDefaultPlaceholder
            wordingTemplate={modelTemplate}
            onPressTemplateButton={logHasClickedGenerateTemplateDescription}
          />
        </FormLayout.Row>
        {isTemplate && (
          <FormLayout.Row className={styles['price-detail']}>
            <TextArea
              disabled={disableForm}
              label="Indiquez le tarif de votre offre"
              maxLength={MAX_PRICE_DETAILS_LENGTH}
              {...register('priceDetail')}
              error={getFieldState('priceDetail').error?.message}
              description="Exemple : par élève ou par groupe scolaire, politique tarifaire REP/REP+ et accompagnateurs..."
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row>
          <TextInput
            label="Indiquez la durée de l’évènement"
            {...register('duration')}
            error={getFieldState('duration').error?.message}
            description="Format : HH:MM"
            disabled={disableForm}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
