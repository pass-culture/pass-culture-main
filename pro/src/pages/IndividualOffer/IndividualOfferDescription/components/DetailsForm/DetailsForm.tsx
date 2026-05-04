import { useFormContext } from 'react-hook-form'

import type {
  CategoryResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { isSubCategoryCD } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/utils'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './DetailsForm.module.scss'
import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { Subcategories } from './Subcategories/Subcategories'

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  hasSelectedProduct: boolean
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readOnlyFields: string[]
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  hasSelectedProduct,
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

  const accessibilityOptions = updateAccessibilityField(setValue, accessibility)

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
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
      </FormLayout.Section>
      <Subcategories
        readOnlyFields={readOnlyFields}
        filteredCategories={filteredCategories}
        filteredSubcategories={filteredSubcategories}
      />
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
