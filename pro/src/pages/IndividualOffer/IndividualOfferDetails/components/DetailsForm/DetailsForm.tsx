import type { ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import type {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { useAccessibilityOptions } from '@/commons/hooks/useAccessibilityOptions'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getAccessibilityInfoFromVenue } from '@/commons/utils/getAccessibilityInfoFromVenue'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './DetailsForm.module.scss'
import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { Subcategories } from './Subcategories/Subcategories'

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  hasSelectedProduct: boolean
  venues: VenueListItemResponseModel[]
  venuesOptions: { label: string; value: string }[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readOnlyFields: string[]
  // TODO (igabriele, 2025-07-24): Remove this prop once the FF is enabled in production.
  withUrlInput?: boolean
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  hasSelectedProduct,
  venues,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
  withUrlInput = false,
}: DetailsFormProps): JSX.Element => {
  const {
    formState: { errors },
    register,
    setValue,
    // trigger,
    watch,
  } = useFormContext<DetailsFormValues>()

  const subcategoryId = watch('subcategoryId')
  const accessibility = watch('accessibility')

  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )
  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId
  const showAddVenueBanner = venuesOptions.length === 0

  const accessibilityOptions = useAccessibilityOptions(setValue, accessibility)

  // TODO (igabriele, 2025-07-16): Use a `watch` flow once the FF is enabled in production.
  const updateVenue = (event: ChangeEvent<HTMLSelectElement>) => {
    if (!isNewOfferCreationFlowFeatureActive && hasSelectedProduct) {
      return
    }

    const venueId = event.target.value
    setValue('venueId', venueId, {
      shouldValidate: true,
    })

    if (!isNewOfferCreationFlowFeatureActive) {
      return
    }

    const venue = venues.find((venue) => venue.id === Number(venueId))
    if (!venue) {
      // TODO (igabriele, 2025-07-16): Handle that more gracefully once we have agreed on how to handle it.
      throw new Error(`Venue with id ${venueId} not found in venues.`)
    }

    const { accessibility } = getAccessibilityInfoFromVenue(venue)
    setValue('accessibility', accessibility)
  }

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row className={styles.row}>
            <Callout
              links={[
                {
                  href: `/inscription/structure/recherche`,
                  icon: {
                    src: fullMoreIcon,
                    alt: '',
                  },
                  label: 'Ajouter une structure',
                },
              ]}
              variant={CalloutVariant.ERROR}
            >
              Pour créer une offre, vous devez d’abord créer une structure.
            </Callout>
          </FormLayout.Row>
        )}
        {!showAddVenueBanner && (
          <>
            {venuesOptions.length > 1 && (
              <FormLayout.Row className={styles.row}>
                <Select
                  label="Qui propose l’offre ? *"
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  {...register('venueId', {
                    onChange: updateVenue,
                  })}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                  error={errors.venueId?.message}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row className={styles.row}>
              <TextInput
                maxCharactersCount={90}
                label="Titre de l’offre"
                {...register('name')}
                error={errors.name?.message}
                required
                disabled={readOnlyFields.includes('name')}
                // This is so browsers don't raise any issue / improvement
                // regarding the existence of an <input type="text" name="name" />
                // that isnt about an user's name to be autofilled.
                autoComplete="false"
              />
            </FormLayout.Row>
            <FormLayout.Row
              sideComponent={<MarkdownInfoBox />}
              className={styles.row}
            >
              <TextArea
                label="Description"
                maxLength={10000}
                {...register('description')}
                disabled={readOnlyFields.includes('description')}
                error={errors.description?.message}
              />
            </FormLayout.Row>
            {!isNewOfferCreationFlowFeatureActive && withUrlInput && (
              <FormLayout.Row className={styles.row}>
                <TextInput
                  label="URL d’accès à l’offre"
                  description="Format : https://exemple.com"
                  disabled={readOnlyFields.includes('url')}
                  {...register('url')}
                  error={errors.url?.message}
                  required
                  type="url"
                />
              </FormLayout.Row>
            )}
          </>
        )}
      </FormLayout.Section>
      {!showAddVenueBanner && (
        <Subcategories
          readOnlyFields={readOnlyFields}
          filteredCategories={filteredCategories}
          filteredSubcategories={filteredSubcategories}
        />
      )}
      {isSubCategorySelected && (
        <DetailsSubForm
          isEanSearchDisplayed={isEanSearchDisplayed}
          isProductBased={hasSelectedProduct}
          isOfferCD={isSubCategoryCD(subcategoryId)}
          readOnlyFields={readOnlyFields}
        />
      )}
      {isNewOfferCreationFlowFeatureActive && accessibilityOptions && (
        <FormLayout.Section title="Modalités d’accessibilité">
          <FormLayout.Row>
            <CheckboxGroup
              options={accessibilityOptions}
              disabled={readOnlyFields.includes('accessibility')}
              label="Cette offre est accessible au public en situation de handicap :"
              description="Sélectionnez au moins une option"
              variant="detailed"
              error={errors.accessibility?.message}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}
    </>
  )
}
