import { useFormContext } from 'react-hook-form'

import { ArtistType } from '@/apiClient/v1'
import { showOptionsTree } from '@/commons/core/Offers/categoriesSubTypes'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullNextIcon from '@/icons/full-next.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildShowSubTypeOptions,
  hasMusicType,
} from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Select } from '@/ui-kit/form/Select/Select'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

import { ArtistField } from './components/ArtistField/ArtistField'
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
  'showSubType',
  'gtl_id',
  'artistOfferLinks',
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

  const { musicTypes } = useMusicTypes()

  const musicTypesOptions = musicTypes.map((data) => ({
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

  const isOfferArtistsFeatureActive = useActiveFeature('WIP_OFFER_ARTISTS')

  const shouldUseArtistOfferLinks =
    isOfferArtistsFeatureActive && !isProductBased

  return (
    <>
      <div role="alert">
        {displayRedirectionCallout && (
          <div className={styles.callout}>
            <Banner
              title="EAN requis"
              actions={[
                {
                  href: '#eanSearch',
                  label: 'Scanner ou rechercher un produit par EAN',
                  type: 'link',
                  icon: fullNextIcon,
                },
              ]}
              variant={BannerVariants.ERROR}
              description="Cette catégorie nécessite un code EAN."
            />
          </div>
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
                    maxCharactersCount={1000}
                    disabled={readOnlyFields.includes('speaker')}
                    {...register('speaker')}
                    error={errors.speaker?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('author') &&
                  !shouldUseArtistOfferLinks && (
                    <TextInput
                      label="Auteur"
                      maxCharactersCount={1000}
                      disabled={readOnlyFields.includes('author')}
                      {...register('author')}
                      error={errors.author?.message}
                    />
                  )}
                {subcategoryConditionalFields.includes('author') &&
                  shouldUseArtistOfferLinks && (
                    <ArtistField
                      readOnly={readOnlyFields.includes('author')}
                      artistType={ArtistType.AUTHOR}
                    />
                  )}
                {subcategoryConditionalFields.includes('visa') && (
                  <TextInput
                    label="Visa d’exploitation"
                    maxCharactersCount={1000}
                    disabled={readOnlyFields.includes('visa')}
                    {...register('visa')}
                    error={errors.visa?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('stageDirector') &&
                  !shouldUseArtistOfferLinks && (
                    <TextInput
                      label="Metteur en scène"
                      maxCharactersCount={1000}
                      disabled={readOnlyFields.includes('stageDirector')}
                      {...register('stageDirector')}
                      error={errors.stageDirector?.message}
                    />
                  )}
                {subcategoryConditionalFields.includes('stageDirector') &&
                  shouldUseArtistOfferLinks && (
                    <ArtistField
                      readOnly={readOnlyFields.includes('stageDirector')}
                      artistType={ArtistType.STAGE_DIRECTOR}
                    />
                  )}
                {subcategoryConditionalFields.includes('performer') &&
                  !shouldUseArtistOfferLinks && (
                    <TextInput
                      label="Interprète"
                      maxCharactersCount={1000}
                      disabled={readOnlyFields.includes('performer')}
                      {...register('performer')}
                      error={errors.performer?.message}
                    />
                  )}
                {subcategoryConditionalFields.includes('performer') &&
                  shouldUseArtistOfferLinks && (
                    <ArtistField
                      readOnly={readOnlyFields.includes('performer')}
                      artistType={ArtistType.PERFORMER}
                    />
                  )}
                {displayEanField && (
                  <TextInput
                    label="EAN-13 (European Article Numbering)"
                    maxCharactersCount={13}
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
