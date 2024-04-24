import { FormikProvider, useFormik } from 'formik'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { GetVenueResponseModel, StudentLevels } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { GET_VENUE_QUERY_KEY } from 'config/swrQueryKeys'
import {
  DEFAULT_MARSEILLE_STUDENTS,
  handleAllFranceDepartmentOptions,
} from 'core/shared'
import { venueInterventionOptions } from 'core/shared/interventionOptions'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { RouteLeavingGuardVenueEdition } from 'pages/VenueEdition/RouteLeavingGuardVenueEdition'
import { Select, TextArea, TextInput } from 'ui-kit'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { MultiSelectAutocomplete } from 'ui-kit/form/MultiSelectAutoComplete/MultiSelectAutocomplete'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'
import { SubmitButton } from 'ui-kit/SubmitButton/SubmitButton'

import editVenueCollectiveDataAdapter from '../adapters/editVenueCollectiveDataAdapter'

import styles from './CollectiveDataForm.module.scss'
import { CollectiveDataFormValues } from './type'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { validationSchema } from './validationSchema'

type CollectiveDataFormProps = {
  statuses: SelectOption[]
  domains: SelectOption[]
  culturalPartners: SelectOption[]
  venue: GetVenueResponseModel
}

const studentLevels = Object.entries(StudentLevels).map(([value, label]) => ({
  value,
  label,
}))

export const CollectiveDataForm = ({
  statuses,
  domains,
  culturalPartners,
  venue,
}: CollectiveDataFormProps): JSX.Element | null => {
  const notify = useNotification()
  const navigate = useNavigate()

  const { mutate } = useSWRConfig()

  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)
  const initialValues = extractInitialValuesFromVenue(venue)

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const studentOptions = isMarseilleEnabled
    ? studentLevels
    : studentLevels.filter(
        (level) => !DEFAULT_MARSEILLE_STUDENTS.includes(level.label)
      )

  const onSubmit = async (values: CollectiveDataFormValues) => {
    const response = await editVenueCollectiveDataAdapter({
      venueId: venue.id,
      values,
    })

    if (!response.isOk) {
      notify.error(response.message)
    }

    await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

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

  return (
    <>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout fullWidthActions>
            <FormLayout.Section title="Vos informations pour les enseignants">
              <FormLayout.SubSection
                title="Présentation pour les enseignants"
                description={
                  venue.isVirtual
                    ? undefined
                    : 'Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité.'
                }
              >
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
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>

              <FormLayout.SubSection title="Informations du lieu">
                <FormLayout.Row>
                  <MultiSelectAutocomplete
                    hideTags
                    options={domains}
                    name="collectiveDomains"
                    label="Domaine artistique et culturel"
                    placeholder="Sélectionner un ou plusieurs domaine(s)"
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
                    placeholder="Association, établissement public..."
                    isOptional
                  />
                </FormLayout.Row>

                <FormLayout.Row>
                  <MultiSelectAutocomplete
                    options={culturalPartners}
                    name="collectiveNetwork"
                    label="Réseaux partenaires EAC"
                    placeholder="Sélectionner un ou plusieurs réseau(x) partenaire(s)"
                    isOptional
                    maxDisplayOptions={20}
                    maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                    hideTags
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>

              <FormLayout.SubSection title="Contact">
                <FormLayout.Row>
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
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>
            </FormLayout.Section>
          </FormLayout>

          <div className={styles['action-bar']}>
            <ButtonLink
              variant={ButtonVariant.SECONDARY}
              link={{
                to: `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/eac`,
                isExternal: false,
              }}
            >
              Annuler et quitter
            </ButtonLink>
            <SubmitButton isLoading={formik.isSubmitting}>
              Enregistrer et quitter
            </SubmitButton>
          </div>
        </form>
      </FormikProvider>

      <RouteLeavingGuardVenueEdition
        shouldBlock={formik.dirty && !formik.isSubmitting}
      />
    </>
  )
}
