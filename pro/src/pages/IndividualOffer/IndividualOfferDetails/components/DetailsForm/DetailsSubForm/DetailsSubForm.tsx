import { useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'
import {
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { HeadlineOfferVideoBanner } from 'components/HeadlineOfferVideoBanner/HeadlineOfferVideoBanner'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildShowSubTypeOptions,
  hasMusicType,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { TimePicker } from 'ui-kit/formV2/TimePicker/TimePicker'

import { ImageUploaderOffer } from '../ImageUploaderOffer/ImageUploaderOffer'

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
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
}

export const DetailsSubForm = ({
  isEanSearchDisplayed,
  isProductBased,
  isOfferCD,
  readOnlyFields,
  onImageUpload,
  onImageDelete,
  imageOffer,
}: DetailsSubFormProps) => {
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const queryOfferType = queryParams.get('offer-type')
  const shouldDisplayVideoBanner =
    queryOfferType === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT ||
    queryOfferType === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT

  const mode = useOfferWizardMode()

  const form = useFormContext()
  const categoryId = form.watch('categoryId')
  const showType = form.watch('showType')
  const subcategoryConditionalFields = form.watch(
    'subcategoryConditionalFields'
  )

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
  const displayImageUploader = !isProductBased || imageOffer
  const displayArtisticInformations = ARTISTIC_INFORMATION_FIELDS.some(
    (field) => subcategoryConditionalFields.includes(field)
  )

  const displayEanField =
    subcategoryConditionalFields.includes('ean') &&
    (mode === OFFER_WIZARD_MODE.CREATION ? !isProductBased : true)

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
          {displayImageUploader && (
            <ImageUploaderOffer
              onImageUpload={onImageUpload}
              onImageDelete={onImageDelete}
              imageOffer={imageOffer}
              hideActionButtons={isProductBased}
            />
          )}

          {shouldDisplayVideoBanner && <HeadlineOfferVideoBanner />}

          {displayArtisticInformations && (
            <FormLayout.Section title="Informations artistiques">
              {hasMusicType(categoryId, subcategoryConditionalFields) && (
                <FormLayout.Row>
                  <Select
                    label="Genre musical"
                    options={musicTypesOptions}
                    defaultOption={{
                      label: 'Choisir un genre musical',
                      value: DEFAULT_DETAILS_FORM_VALUES.gtl_id,
                    }}
                    disabled={readOnlyFields.includes('gtl_id')}
                    {...form.register('gtl_id')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('showType') && (
                <>
                  <FormLayout.Row>
                    <Select
                      label="Type de spectacle"
                      options={showTypesOptions}
                      defaultOption={{
                        label: 'Choisir un type de spectacle',
                        value: DEFAULT_DETAILS_FORM_VALUES.showType,
                      }}
                      disabled={readOnlyFields.includes('showType')}
                      {...form.register('showType')}
                      required
                    />
                  </FormLayout.Row>
                  <FormLayout.Row>
                    <Select
                      label="Sous-type"
                      options={showSubTypeOptions}
                      defaultOption={{
                        label: 'Choisir un sous-type',
                        value: DEFAULT_DETAILS_FORM_VALUES.showSubType,
                      }}
                      disabled={readOnlyFields.includes('showSubType')}
                      {...form.register('showSubType')}
                      required
                    />
                  </FormLayout.Row>
                </>
              )}
              {subcategoryConditionalFields.includes('speaker') && (
                <FormLayout.Row>
                  <TextInput
                    label="Intervenant"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('speaker')}
                    {...form.register('speaker')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('author') && (
                <FormLayout.Row>
                  <TextInput
                    label="Auteur"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('author')}
                    {...form.register('author')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('visa') && (
                <FormLayout.Row>
                  <TextInput
                    label="Visa d’exploitation"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('visa')}
                    {...form.register('visa')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('stageDirector') && (
                <FormLayout.Row>
                  <TextInput
                    label="Metteur en scène"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('stageDirector')}
                    {...form.register('stageDirector')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('performer') && (
                <FormLayout.Row>
                  <TextInput
                    label="Interprète"
                    maxLength={1000}
                    disabled={readOnlyFields.includes('performer')}
                    {...form.register('performer')}
                  />
                </FormLayout.Row>
              )}
              {displayEanField && (
                <FormLayout.Row>
                  <TextInput
                    label="EAN-13 (European Article Numbering)"
                    count={form.watch('ean').length}
                    maxLength={13}
                    disabled={readOnlyFields.includes('ean')}
                    {...form.register('ean')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('durationMinutes') && (
                <FormLayout.Row>
                  <TimePicker
                    label="Durée"
                    disabled={readOnlyFields.includes('durationMinutes')}
                    suggestedTimeList={{
                      min: '00:00',
                      max: '04:00',
                    }}
                    {...form.register('durationMinutes')}
                  />
                </FormLayout.Row>
              )}
            </FormLayout.Section>
          )}
        </div>
      )}
    </>
  )
}
