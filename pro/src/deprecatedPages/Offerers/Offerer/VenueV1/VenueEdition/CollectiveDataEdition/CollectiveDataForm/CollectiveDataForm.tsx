import { FormikProvider, useFormik } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { GetCollectiveVenueResponseModel, StudentLevels } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import {
  EducationalCategories,
  IEducationalSubCategory,
} from 'core/OfferEducational'
import { handleAllFranceDepartmentOptions } from 'core/shared'
import { venueInterventionOptions } from 'core/shared/interventionOptions'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import {
  MultiSelectAutocomplete,
  Select,
  SubmitButton,
  TextArea,
  TextInput,
} from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import editVenueCollectiveDataAdapter from '../adapters/editVenueCollectiveDataAdapter'
import RouteLeavingGuardVenueCollectiveDataEdition from '../RouteLeavingGuardVenueCollectiveDataEdition'

import styles from './CollectiveDataForm.module.scss'
import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from './initialValues'
import { CollectiveDataFormValues } from './type'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { validationSchema } from './validationSchema'

const studentOptions = [
  { value: StudentLevels.COLL_GE_4E, label: StudentLevels.COLL_GE_4E },
  { value: StudentLevels.COLL_GE_3E, label: StudentLevels.COLL_GE_3E },
  { value: StudentLevels.CAP_1RE_ANN_E, label: StudentLevels.CAP_1RE_ANN_E },
  { value: StudentLevels.CAP_2E_ANN_E, label: StudentLevels.CAP_2E_ANN_E },
  { value: StudentLevels.LYC_E_SECONDE, label: StudentLevels.LYC_E_SECONDE },
  { value: StudentLevels.LYC_E_PREMI_RE, label: StudentLevels.LYC_E_PREMI_RE },
  {
    value: StudentLevels.LYC_E_TERMINALE,
    label: StudentLevels.LYC_E_TERMINALE,
  },
]

type CollectiveDataFormProps = {
  statuses: SelectOption[]
  domains: SelectOption[]
  culturalPartners: SelectOption[]
  venueId: string
  offererId: string
  venueCollectiveData: GetCollectiveVenueResponseModel | null
  adageVenueCollectiveData: GetCollectiveVenueResponseModel | null
  categories: EducationalCategories
}

const getCategoriesAndSubcategoriesOptions = (
  categories: EducationalCategories,
  availableSubCategories: IEducationalSubCategory[]
) => {
  let categoriesOptions = categories.educationalCategories.map(item => ({
    value: item['id'],
    label: item['label'],
  }))
  if (categoriesOptions.length > 1) {
    categoriesOptions = [
      { value: '', label: 'Sélectionner une catégorie' },
      ...categoriesOptions,
    ]
  }

  let subCategoriesOptions = availableSubCategories.map(item => ({
    value: item['id'],
    label: item['label'],
  }))

  if (subCategoriesOptions.length > 1) {
    subCategoriesOptions = [
      { value: '', label: 'Sélectionner une sous catégorie' },
      ...subCategoriesOptions,
    ]
  }
  return {
    categoriesOptions,
    subCategoriesOptions,
  }
}

const CollectiveDataForm = ({
  statuses,
  domains,
  culturalPartners,
  venueId,
  offererId,
  venueCollectiveData,
  adageVenueCollectiveData,
  categories,
}: CollectiveDataFormProps): JSX.Element | null => {
  const notify = useNotification()
  const navigate = useNavigate()

  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)

  const initialValues = venueCollectiveData
    ? extractInitialValuesFromVenue(venueCollectiveData, categories)
    : COLLECTIVE_DATA_FORM_INITIAL_VALUES

  const [availableSubCategories, setAvailableSubCategories] = useState<
    IEducationalSubCategory[]
  >(
    initialValues.collectiveCategoryId
      ? categories.educationalSubCategories.filter(
          x => x.categoryId == initialValues.collectiveCategoryId
        )
      : []
  )

  const onSubmit = async (values: CollectiveDataFormValues) => {
    setIsLoading(true)
    setIsClickingFromActionBar(true)
    const response = await editVenueCollectiveDataAdapter({
      venueId: Number(venueId),
      values,
    })

    if (!response.isOk) {
      notify.error(response.message)
      setIsClickingFromActionBar(false)
      return setIsLoading(false)
    }

    formik.resetForm({
      values: extractInitialValuesFromVenue(response.payload, categories),
    })

    navigate(`/structures/${offererId}/lieux/${venueId}`, {
      state: {
        collectiveDataEditionSuccess: response.message,
        scrollToElementId: 'venue-collective-data',
      },
    })
  }

  const formik = useFormik<CollectiveDataFormValues>({
    initialValues: initialValues,
    onSubmit: onSubmit,
    validationSchema,
  })
  useEffect(() => {
    handleAllFranceDepartmentOptions(
      formik.values.collectiveInterventionArea,
      previousInterventionValues,
      (value: string[]) =>
        formik.setFieldValue('collectiveInterventionArea', value)
    )

    setPreviousInterventionValues(formik.values.collectiveInterventionArea)
  }, [formik.values.collectiveInterventionArea])

  useEffect(() => {
    formik.resetForm({
      values: venueCollectiveData
        ? extractInitialValuesFromVenue(venueCollectiveData, categories)
        : COLLECTIVE_DATA_FORM_INITIAL_VALUES,
    })
  }, [venueCollectiveData])

  useEffect(() => {
    if (adageVenueCollectiveData && categories) {
      formik.setValues(
        extractInitialValuesFromVenue(adageVenueCollectiveData, categories)
      )
    }
  }, [adageVenueCollectiveData, categories])

  const handleCategoryChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const newCategoryId = event.target.value

      setAvailableSubCategories(
        categories.educationalSubCategories.filter(
          subCategory => subCategory.categoryId === newCategoryId
        )
      )
    },
    [categories.educationalSubCategories]
  )

  const { categoriesOptions, subCategoriesOptions } =
    getCategoriesAndSubcategoriesOptions(categories, availableSubCategories)

  return (
    <>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <div className={styles.form}>
            <div className={styles.section}>
              Présentation pour les enseignants
            </div>

            <FormLayout.Row>
              <TextArea
                name="collectiveDescription"
                label="Démarche d’éducation artistique et culturelle"
                placeholder="Présenter la démarche d’éducation artistique et culturelle : présentation du lieu, actions menées auprès du public scolaire..."
                maxLength={500}
                countCharacters
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <MultiSelectAutocomplete
                name="collectiveStudents"
                label="Public cible"
                options={studentOptions}
                placeholder="Sélectionner un public cible"
                className={styles.row}
                hideTags
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                name="collectiveWebsite"
                label="URL de votre site web"
                placeholder="https://exemple.com"
                isOptional
                className={styles.row}
              />
            </FormLayout.Row>
            <div className={styles.section}>Informations du lieu</div>
            <FormLayout.Row>
              <Select
                label="Catégorie"
                name="collectiveCategoryId"
                options={categoriesOptions}
                onChange={handleCategoryChange}
                isOptional={true}
              />
            </FormLayout.Row>
            {availableSubCategories.length > 0 && (
              <FormLayout.Row>
                <Select
                  label="Sous-catégorie"
                  name="collectiveSubCategoryId"
                  options={subCategoriesOptions}
                  isOptional={true}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row>
              <MultiSelectAutocomplete
                hideTags
                options={domains}
                name="collectiveDomains"
                label="Domaine artistique et culturel"
                placeholder="Sélectionner un ou plusieurs domaine(s)"
                className={styles.row}
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <MultiSelectAutocomplete
                hideTags
                options={venueInterventionOptions}
                name="collectiveInterventionArea"
                label="Zone de mobilité"
                placeholder="Sélectionner une ou plusieurs zone(s) de mobilité"
                className={styles.row}
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <Select
                options={[
                  { value: '', label: 'Sélectionner un statut' },
                  ...statuses,
                ]}
                name="collectiveLegalStatus"
                label="Statut"
                className={styles.row}
                placeholder="Association, établissement public..."
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <MultiSelectAutocomplete
                options={culturalPartners}
                name="collectiveNetwork"
                label="Réseaux partenaires EAC"
                className={styles.row}
                placeholder="Sélectionner un ou plusieurs réseau(x) partenaire(s)"
                isOptional
                maxDisplayOptions={20}
                maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                hideTags
              />
            </FormLayout.Row>
            <div className={styles.contact}>Contact</div>
            <FormLayout.Row className={styles.phone}>
              <PhoneNumberInput
                name="collectivePhone"
                label="Téléphone"
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                name="collectiveEmail"
                label="E-mail"
                placeholder="email@exemple.com"
                isOptional
                className={styles.row}
              />
            </FormLayout.Row>
          </div>
          <FormLayout.Actions>
            <Link
              className="secondary-link"
              state={{ scrollToElementId: 'venue-collective-data' }}
              to={`/structures/${offererId}/lieux/${venueId}`}
            >
              Annuler et quitter
            </Link>
            <SubmitButton isLoading={isLoading}>Enregistrer</SubmitButton>
          </FormLayout.Actions>
        </form>
      </FormikProvider>
      <RouteLeavingGuardVenueCollectiveDataEdition
        shouldBlock={formik.dirty && !isClickingFromActionBar}
      />
    </>
  )
}

export default CollectiveDataForm
