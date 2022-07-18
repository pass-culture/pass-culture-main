import { FormikProvider, useFormik } from 'formik'
import { GetCollectiveVenueResponseModel, StudentLevels } from 'apiClient/v1'
import { Link, useHistory } from 'react-router-dom'
import {
  MultiSelectAutocomplete,
  Select,
  SubmitButton,
  TextArea,
  TextInput,
} from 'ui-kit'
import React, { useEffect, useState } from 'react'

import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from './initialValues'
import { CollectiveDataFormValues } from './type'
import FormLayout from 'new_components/FormLayout'
import RouteLeavingGuardVenueCollectiveDataEdition from '../RouteLeavingGuardVenueCollectiveDataEdition'
import { SelectOption } from 'custom_types/form'
import editVenueCollectiveDataAdapter from '../adapters/editVenueCollectiveDataAdapter'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { handleAllFranceDepartmentOptions } from './utils/handleAllFranceDepartmentOptions'
import { interventionOptions } from 'core/Venue'
import styles from './CollectiveDataForm.module.scss'
import useNotification from 'components/hooks/useNotification'
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
}

const CollectiveDataForm = ({
  statuses,
  domains,
  culturalPartners,
  venueId,
  offererId,
  venueCollectiveData,
}: CollectiveDataFormProps): JSX.Element => {
  const notify = useNotification()
  const history = useHistory()

  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)
  const [isLoading, setIsLoading] = useState(false)

  const onSubmit = async (values: CollectiveDataFormValues) => {
    setIsLoading(true)
    const response = await editVenueCollectiveDataAdapter({ venueId, values })

    if (!response.isOk) {
      notify.error(response.message)
      return setIsLoading(false)
    }

    formik.resetForm({
      values: extractInitialValuesFromVenue(response.payload),
    })

    history.push({
      pathname: `/structures/${offererId}/lieux/${venueId}`,
      state: {
        collectiveDataEditionSuccess: response.message,
      },
    })
  }

  const formik = useFormik<CollectiveDataFormValues>({
    initialValues: venueCollectiveData
      ? extractInitialValuesFromVenue(venueCollectiveData)
      : COLLECTIVE_DATA_FORM_INITIAL_VALUES,
    onSubmit: onSubmit,
    validationSchema,
  })

  useEffect(() => {
    formik.resetForm({
      values: venueCollectiveData
        ? extractInitialValuesFromVenue(venueCollectiveData)
        : COLLECTIVE_DATA_FORM_INITIAL_VALUES,
    })
  }, [venueCollectiveData])

  useEffect(() => {
    handleAllFranceDepartmentOptions(
      formik.values.collectiveInterventionArea,
      previousInterventionValues,
      formik.setFieldValue
    )

    setPreviousInterventionValues(formik.values.collectiveInterventionArea)
  }, [formik.values.collectiveInterventionArea])

  return (
    <>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
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
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              fieldName="collectiveStudents"
              label="Public cible :"
              options={studentOptions}
              placeholder="Sélectionner un public cible"
              inline
              className={styles.row}
              hideTags
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              name="collectiveWebsite"
              label="URL de votre site web :"
              placeholder="http://exemple.com"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
          <div className={styles.section}>Informations du lieu</div>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              hideTags
              options={domains}
              fieldName="collectiveDomains"
              label="Domaine artistique et culturel :"
              placeholder="Sélectionner un ou plusieurs domaine(s)"
              className={styles.row}
              inline
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              hideTags
              options={interventionOptions}
              fieldName="collectiveInterventionArea"
              label="Périmètre d’intervention :"
              placeholder="Sélectionner un ou plusieurs territoire(s) d'intervention"
              className={styles.row}
              inline
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <Select
              options={[
                { value: '', label: 'Sélectionner un statut' },
                ...statuses,
              ]}
              name="collectiveLegalStatus"
              label="Statut :"
              className={styles.row}
              placeholder="Association, établissement public..."
              inline
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              options={culturalPartners}
              fieldName="collectiveNetwork"
              label="Réseaux partenaires EAC  :"
              className={styles.row}
              placeholder="Sélectionner un ou plusieurs réseau(x) partenaire(s)"
              inline
              maxDisplayOptions={20}
              maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
              hideTags
            />
          </FormLayout.Row>
          <div className={styles.section}>Contact pour les enseignants</div>
          <FormLayout.Row>
            <TextInput
              name="collectivePhone"
              label="Téléphone :"
              placeholder="0612345678"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              name="collectiveEmail"
              label="E-mail :"
              placeholder="email@exemple.com"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
          <FormLayout.Actions>
            <Link
              className="secondary-link"
              to={`/structures/${offererId}/lieux/${venueId}`}
            >
              Annuler et quitter
            </Link>
            <SubmitButton isLoading={isLoading} disabled={!formik.dirty}>
              Enregistrer
            </SubmitButton>
          </FormLayout.Actions>
        </form>
      </FormikProvider>
      <RouteLeavingGuardVenueCollectiveDataEdition isFormDirty={formik.dirty} />
    </>
  )
}

export default CollectiveDataForm
