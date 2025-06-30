import { useFormContext } from 'react-hook-form'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildShowSubTypeOptions,
  hasMusicType,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

import styles from './DetailsSubForm.module.scss'

export const ARTISTIC_INFORMATION_FIELDS: (keyof DetailsFormValues)[] = [
  'speaker',
  'author',
  'visa',
  'stageDirector',
  'performer',
  'ean',
  'durationMinutes',
  'showType',
  'gtl_id',
]

export type DetailsSubFormProps = {
  isEanSearchDisplayed: boolean
  isProductBased: boolean
  isOfferCD: boolean
  readOnlyFields: string[]
}

export const DetailsSubForm = ({
  isEanSearchDisplayed,
  isProductBased,
  isOfferCD,
  readOnlyFields,
}: DetailsSubFormProps) => {
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const categoryId = watch('categoryId')
  const showType = watch('showType')
  const subcategoryConditionalFields = watch('subcategoryConditionalFields')

  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const musicTypesOptions = musicTypesQuery.data.map((data) => ({
    value: data.gtl_id,
    label: data.label,
  }))

  const showTypesOptions = showOptionsTree
    .map((data) => ({
      label: data.label,
      value: data.code.toString(),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

  const showSubTypeOptions = buildShowSubTypeOptions(showType)

  // In the context of an offer creation, vinyls & CDs must be
  // product-based offers so the form must be pre-filled with
  // the results of an EAN search.
  const displayRedirectionCallout =
    isEanSearchDisplayed && !isProductBased && isOfferCD
  const displayArtisticInformations = ARTISTIC_INFORMATION_FIELDS.some(
    (field) => subcategoryConditionalFields.includes(field)
  )

  const displayEanField =
    subcategoryConditionalFields.includes('ean') && !isEanSearchDisplayed

  return (
    <>
      <div role="alert">
        {displayRedirectionCallout && (
          <Callout
            className={styles.callout}
            links={[
              {
                href: '#eanSearch',
                label: 'Scanner ou rechercher un produit par EAN',
                isSectionLink: true,
              },
            ]}
            variant={CalloutVariant.ERROR}
          >
            Cette catégorie nécessite un EAN.
          </Callout>
        )}
      </div>
      {!displayRedirectionCallout && (
        <div className={styles['sub-form']}>
          {displayArtisticInformations && (
            <FormLayout.Section title="Informations artistiques">
              <div className={styles['artistic-info-inputs']}>
                {hasMusicType(categoryId, subcategoryConditionalFields) && (
                  <Select
                    label="Genre musical"
                    options={musicTypesOptions}
                    required
                    defaultOption={{
                      label: 'Choisir un genre musical',
                      value: DEFAULT_DETAILS_FORM_VALUES.gtl_id,
                    }}
                    disabled={readOnlyFields.includes('gtl_id')}
                    {...register('gtl_id')}
                    error={errors.gtl_id?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('showType') && (
                  <>
                    <Select
                      label="Type de spectacle"
                      options={showTypesOptions}
                      defaultOption={{
                        label: 'Choisir un type de spectacle',
                        value: DEFAULT_DETAILS_FORM_VALUES.showType,
                      }}
                      disabled={readOnlyFields.includes('showType')}
                      {...register('showType')}
                      error={errors.showType?.message}
                      required
                    />
                    <Select
                      label="Sous-type"
                      options={showSubTypeOptions}
                      defaultOption={{
                        label: 'Choisir un sous-type',
                        value: DEFAULT_DETAILS_FORM_VALUES.showSubType,
                      }}
                      disabled={readOnlyFields.includes('showSubType')}
                      {...register('showSubType')}
                      error={errors.showSubType?.message}
                      required
                    />
                  </>
                )}
                {subcategoryConditionalFields.includes('speaker') && (
                  <TextInput
                    label="Intervenant"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('speaker')}
                    {...register('speaker')}
                    error={errors.speaker?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('author') && (
                  <TextInput
                    label="Auteur"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('author')}
                    {...register('author')}
                    error={errors.author?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('visa') && (
                  <TextInput
                    label="Visa d’exploitation"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('visa')}
                    {...register('visa')}
                    error={errors.visa?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('stageDirector') && (
                  <TextInput
                    label="Metteur en scène"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('stageDirector')}
                    {...register('stageDirector')}
                    error={errors.stageDirector?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('performer') && (
                  <TextInput
                    label="Interprète"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('performer')}
                    {...register('performer')}
                    error={errors.performer?.message}
                  />
                )}
                {displayEanField && (
                  <TextInput
                    label="EAN-13 (European Article Numbering)"
                    count={watch('ean')?.length}
                    maxLength={13}
                    disabled={readOnlyFields.includes('ean')}
                    {...register('ean')}
                    error={errors.ean?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('durationMinutes') && (
                  <TimePicker
                    label="Durée"
                    disabled={readOnlyFields.includes('durationMinutes')}
                    suggestedTimeList={{
                      min: '00:00',
                      max: '04:00',
                    }}
                    {...register('durationMinutes')}
                    error={errors.durationMinutes?.message}
                  />
                )}
              </div>
            </FormLayout.Section>
          )}
        </div>
      )}
    </>
  )
}
