import { liteClient } from 'algoliasearch/lite'
import { useFormContext } from 'react-hook-form'
import {
  Configure,
  Index,
  InstantSearch,
  useHits,
  useSearchBox,
} from 'react-instantsearch'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_MUSIC_TYPES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { showOptionsTree } from '@/commons/core/Offers/categoriesSubTypes'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_INDIVIDUAL_OFFERS_ARTISTS_INDEX,
} from '@/commons/utils/config'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildShowSubTypeOptions,
  hasMusicType,
} from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { Select } from '@/ui-kit/form/Select/Select'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

import styles from './DetailsSubForm.module.scss'

const searchClient = liteClient(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

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
                    maxCharactersCount={1000}
                    disabled={readOnlyFields.includes('speaker')}
                    {...register('speaker')}
                    error={errors.speaker?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('author') && (
                  <AuthorWithAlgolia />
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
                {subcategoryConditionalFields.includes('stageDirector') && (
                  <TextInput
                    label="Metteur en scène"
                    maxCharactersCount={1000}
                    disabled={readOnlyFields.includes('stageDirector')}
                    {...register('stageDirector')}
                    error={errors.stageDirector?.message}
                  />
                )}
                {subcategoryConditionalFields.includes('performer') && (
                  <TextInput
                    label="Interprète"
                    maxCharactersCount={1000}
                    disabled={readOnlyFields.includes('performer')}
                    {...register('performer')}
                    error={errors.performer?.message}
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

function AuthorSearchField() {
  const {
    register,
    setValue,
    watch,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const author = watch('author') ?? ''
  const { refine } = useSearchBox()
  const { hits } = useHits<{ objectID: string; name: string }>()

  // Afficher les suggestions seulement si on a du texte + des résultats
  const showSuggestions = author.trim().length > 0 && hits.length > 0

  // Propager la frappe à Algolia en temps réel
  const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const v = e.target.value
    setValue('author', v, { shouldValidate: false, shouldDirty: true })
    refine(v)
  }

  // Cliquer remplit le champ et vide la query pour masquer la liste
  const handlePick = (name: string) => {
    setValue('author', name, { shouldValidate: true, shouldDirty: true })
    refine('') // masque les résultats
  }

  return (
    <div>
      <TextInput
        label="Auteur"
        maxCharactersCount={1000}
        {...register('author')}
        // onChange contrôlé pour alimenter Algolia
        onChange={handleChange}
        error={errors.author?.message}
      />

      {showSuggestions && (
        <div
          // Simple panneau texte pour la démo
          style={{
            marginTop: 8,
            border: '1px solid var(--grey-300, #ddd)',
            padding: 8,
            borderRadius: 6,
            background: 'var(--bg, #fff)',
          }}
          role="listbox"
        >
          <ul>
            {hits.map((hit) => (
              <li
                key={hit.objectID}
                // onMouseDown évite que le blur du champ annule le clic
                onMouseDown={(e) => {
                  e.preventDefault()
                  handlePick(hit.name)
                }}
                style={{
                  cursor: 'pointer',
                  padding: '6px 4px',
                }}
              >
                {hit.name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export function AuthorWithAlgolia() {
  return (
    <InstantSearch
      indexName={ALGOLIA_INDIVIDUAL_OFFERS_ARTISTS_INDEX}
      searchClient={searchClient}
      future={{ preserveSharedStateOnUnmount: true }}
    >
      <Index indexName={ALGOLIA_INDIVIDUAL_OFFERS_ARTISTS_INDEX}>
        <Configure
          attributesToHighlight={[]}
          attributesToRetrieve={['name']}
          hitsPerPage={8}
        />
        <AuthorSearchField />
      </Index>
    </InstantSearch>
  )
}
