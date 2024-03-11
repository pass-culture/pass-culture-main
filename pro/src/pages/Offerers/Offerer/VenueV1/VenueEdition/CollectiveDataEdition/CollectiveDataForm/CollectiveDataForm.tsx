import { FormikProvider, useFormik } from 'formik'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  GetCollectiveVenueResponseModel,
  GetVenueResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import FormLayout from 'components/FormLayout'
import { handleAllFranceDepartmentOptions } from 'core/shared'
import { venueInterventionOptions } from 'core/shared/interventionOptions'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { ButtonLink, Select, SubmitButton, TextArea, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { MultiSelectAutocomplete } from 'ui-kit/form/MultiSelectAutoComplete/MultiSelectAutocomplete'
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
  venue: GetVenueResponseModel
  venueCollectiveData: GetCollectiveVenueResponseModel | null
  adageVenueCollectiveData: GetCollectiveVenueResponseModel | null
  reloadVenueData: () => Promise<void>
}

const CollectiveDataForm = ({
  statuses,
  domains,
  culturalPartners,
  venue,
  venueCollectiveData,
  adageVenueCollectiveData,
  reloadVenueData,
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
    ? extractInitialValuesFromVenue(venueCollectiveData)
    : COLLECTIVE_DATA_FORM_INITIAL_VALUES

  const onSubmit = async (values: CollectiveDataFormValues) => {
    setIsLoading(true)
    setIsClickingFromActionBar(true)
    const response = await editVenueCollectiveDataAdapter({
      venueId: venue.id,
      values,
    })

    if (!response.isOk) {
      notify.error(response.message)
      setIsClickingFromActionBar(false)
      return setIsLoading(false)
    }

    formik.resetForm({
      values: extractInitialValuesFromVenue(response.payload),
    })

    await reloadVenueData()

    navigate(`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/eac`)
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
        ? extractInitialValuesFromVenue(venueCollectiveData)
        : COLLECTIVE_DATA_FORM_INITIAL_VALUES,
    })
  }, [venueCollectiveData])

  useEffect(() => {
    async function setExtractInitialValuesFromVenue() {
      if (adageVenueCollectiveData) {
        await formik.setValues(
          extractInitialValuesFromVenue(adageVenueCollectiveData)
        )
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setExtractInitialValuesFromVenue()
  }, [adageVenueCollectiveData])

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
                label="Email"
                placeholder="email@exemple.com"
                isOptional
                className={styles.row}
              />
            </FormLayout.Row>
          </div>

          <ActionsBarSticky>
            <ActionsBarSticky.Left>
              <ButtonLink
                variant={ButtonVariant.SECONDARY}
                link={{ isExternal: false, to: `/accueil` }}
              >
                Annuler et quitter
              </ButtonLink>
            </ActionsBarSticky.Left>
            <ActionsBarSticky.Right>
              <SubmitButton isLoading={isLoading}>
                Enregistrer et quitter
              </SubmitButton>
            </ActionsBarSticky.Right>
          </ActionsBarSticky>
        </form>
      </FormikProvider>

      <RouteLeavingGuardVenueCollectiveDataEdition
        shouldBlock={formik.dirty && !isClickingFromActionBar}
      />
    </>
  )
}

export default CollectiveDataForm
