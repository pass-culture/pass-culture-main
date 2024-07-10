import { useFormikContext } from 'formik'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ImageUploaderOffer } from 'components/IndividualOfferForm/ImageUploaderOffer/ImageUploaderOffer'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { DurationInput } from 'ui-kit/form/DurationInput/DurationInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'
import { DetailsFormValues } from './types'
import {
  buildCategoryOptions,
  buildSubcategoryOptions,
  buildVenueOptions,
  buildShowSubTypeOptions,
  onSubcategoryChange,
} from './utils'

type DetailsFormProps = {
  filteredVenues: VenueListItemResponseModel[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
}

export const DetailsForm = ({
  filteredVenues,
  filteredCategories,
  filteredSubcategories,
}: DetailsFormProps): JSX.Element => {
  const {
    values: {
      categoryId,
      subcategoryId,
      showType,
      subcategoryConditionalFields,
    },
    handleChange,
    setFieldValue,
  } = useFormikContext<DetailsFormValues>()

  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
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

  const venueOptions = buildVenueOptions(filteredVenues)

  // this condition exists in the original code
  // but it is not clear why it is needed
  const hasMusicType =
    categoryId !== 'LIVRE'
      ? subcategoryConditionalFields.includes('gtl_id')
      : subcategoryConditionalFields.includes('musicType')

  const artisticInformationsFields = [
    'speaker',
    'author',
    'visa',
    'stageDirector',
    'performer',
    'ean',
    'durationMinutes',
  ]

  const displayArtisticInformations = artisticInformationsFields.some((field) =>
    subcategoryConditionalFields.includes(field)
  )

  return (
    <>
      <FormLayout.Section title="A propos de votre offre">
        <FormLayout.Row>
          <TextInput
            countCharacters
            label="Titre de l’offre"
            maxLength={90}
            name="name"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextArea
            countCharacters
            isOptional
            label="Description"
            maxLength={1000}
            name="description"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select label="Lieu" name="venueId" options={venueOptions} />
        </FormLayout.Row>
      </FormLayout.Section>

      <FormLayout.Section title="Type d’offre">
        <FormLayout.Row
          sideComponent={
            <InfoBox
              link={{
                isExternal: true,
                to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
                text: 'Quelles catégories choisir ?',
                opensInNewTab: true,
              }}
            >
              Une sélection précise de vos catégories permettra au grand public
              de facilement trouver votre offre. Une fois validées, vous ne
              pourrez pas les modifier.
            </InfoBox>
          }
        >
          <Select
            label="Catégorie"
            name="categoryId"
            options={categoryOptions}
            defaultOption={{
              label: 'Choisir une catégorie',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.categoryId,
            }}
          />
        </FormLayout.Row>
        {categoryId !== DEFAULT_DETAILS_INTITIAL_VALUES.categoryId && (
          <FormLayout.Row>
            <Select
              label="Sous-catégorie"
              name="subcategoryId"
              options={subcategoryOptions}
              defaultOption={{
                label: 'Choisir une sous-catégorie',
                value: DEFAULT_DETAILS_INTITIAL_VALUES.subcategoryId,
              }}
              onChange={async (event: React.ChangeEvent<HTMLSelectElement>) => {
                await onSubcategoryChange({
                  newSubCategoryId: event.target.value,
                  subcategories: filteredSubcategories,
                  setFieldValue,
                })
                handleChange(event)
              }}
            />
          </FormLayout.Row>
        )}
        {hasMusicType && (
          <FormLayout.Row>
            <Select
              label="Genre musical"
              name="gtl_id"
              options={musicTypesOptions}
              defaultOption={{
                label: 'Choisir un genre musical',
                value: DEFAULT_DETAILS_INTITIAL_VALUES.gtl_id,
              }}
            />
          </FormLayout.Row>
        )}
        {subcategoryConditionalFields.includes('showType') && (
          <>
            <FormLayout.Row>
              <Select
                label="Type de spectacle"
                name="showType"
                options={showTypesOptions}
                defaultOption={{
                  label: 'Choisir un type de spectacle',
                  value: DEFAULT_DETAILS_INTITIAL_VALUES.showType,
                }}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <Select
                label="Sous-type"
                name="showSubType"
                options={showSubTypeOptions}
                defaultOption={{
                  label: 'Choisir un sous-type',
                  value: DEFAULT_DETAILS_INTITIAL_VALUES.showSubType,
                }}
              />
            </FormLayout.Row>
          </>
        )}
      </FormLayout.Section>
      {subcategoryId !== DEFAULT_DETAILS_INTITIAL_VALUES.subcategoryId && (
        <>
          <ImageUploaderOffer
            onImageUpload={async () => {}}
            onImageDelete={async () => {}}
            imageOffer={{
              originalUrl: '',
              url: '',
              credit: '',
            }}
          />

          {displayArtisticInformations && (
            <FormLayout.Section title="Informations artistiques">
              {subcategoryConditionalFields.includes('speaker') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Intervenant"
                    maxLength={1000}
                    name="speaker"
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('author') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Auteur"
                    maxLength={1000}
                    name="author"
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('visa') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Visa d’exploitation"
                    maxLength={1000}
                    name="visa"
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('stageDirector') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Metteur en scène"
                    maxLength={1000}
                    name="stageDirector"
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('performer') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Interprète"
                    maxLength={1000}
                    name="performer"
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('ean') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="EAN-13 (European Article Numbering)"
                    countCharacters
                    name="ean"
                    maxLength={13}
                  />
                </FormLayout.Row>
              )}

              {subcategoryConditionalFields.includes('durationMinutes') && (
                <FormLayout.Row>
                  <DurationInput
                    isOptional
                    label={'Durée'}
                    name="durationMinutes"
                  />
                </FormLayout.Row>
              )}
            </FormLayout.Section>
          )}
        </>
      )}
    </>
  )
}
