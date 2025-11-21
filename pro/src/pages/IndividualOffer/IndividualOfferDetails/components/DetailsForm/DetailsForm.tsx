import type { ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import type {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getAccessibilityInfoFromVenue } from '@/commons/utils/getAccessibilityInfoFromVenue'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
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
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  hasSelectedProduct,
  venues,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
}: DetailsFormProps): JSX.Element => {
  const {
    formState: { errors },
    register,
    setValue,
    watch,
  } = useFormContext<DetailsFormValues>()

  const subcategoryId = watch('subcategoryId')
  const accessibility = watch('accessibility')

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId
  const showAddVenueBanner = venuesOptions.length === 0

  const accessibilityOptions = updateAccessibilityField(setValue, accessibility)

  // TODO (igabriele, 2025-07-16): Use a `watch` flow once the FF is enabled in production.
  const updateVenue = (event: ChangeEvent<HTMLSelectElement>) => {
    const venueId = event.target.value
    setValue('venueId', venueId, {
      shouldValidate: true,
    })

    const venue = venues.find((venue) => venue.id === Number(venueId))
    assertOrFrontendError(
      venue,
      `Venue with id ${venueId} not found in venues.`
    )

    const { accessibility } = getAccessibilityInfoFromVenue(venue)
    setValue('accessibility', accessibility)
  }

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row className={styles.row}>
            <Banner
              title=""
              actions={[
                {
                  href: `/inscription/structure/recherche`,
                  icon: fullMoreIcon,
                  label: 'Ajouter une structure',
                  type: 'link',
                },
              ]}
              variant={BannerVariants.ERROR}
              description="Pour créer une offre, vous devez d’abord créer une structure."
            />
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
      {accessibilityOptions && (
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
