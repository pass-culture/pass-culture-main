import { FormikProvider, useFormik } from 'formik'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel, StudentLevels } from 'apiClient/v1'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  DEFAULT_MARSEILLE_STUDENTS,
  SENT_DATA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { venueInterventionOptions } from 'commons/core/shared/interventionOptions'
import { handleAllFranceDepartmentOptions } from 'commons/core/shared/utils/handleAllFranceDepartmentOptions'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RouteLeavingGuardVenueEdition } from 'pages/VenueEdition/RouteLeavingGuardVenueEdition'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './CollectiveDataForm.module.scss'
import { CollectiveDataFormValues } from './type'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { validationSchema } from './validationSchema'

type CollectiveDataFormProps = {
  statuses: SelectOption[]
  domains: SelectOption[]
  venue: GetVenueResponseModel
}

const studentLevels = Object.entries(StudentLevels).map(([, value]) => ({
  value,
  label: value,
}))

export const CollectiveDataForm = ({
  statuses,
  domains,
  venue,
}: CollectiveDataFormProps): JSX.Element | null => {
  const notify = useNotification()
  const navigate = useNavigate()

  const { mutate } = useSWRConfig()

  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)
  const initialValues = extractInitialValuesFromVenue(venue)

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const studentOptions = isMarseilleEnabled
    ? studentLevels
    : studentLevels.filter(
        (level) => !DEFAULT_MARSEILLE_STUDENTS.includes(level.value)
      )

  const onSubmit = async (values: CollectiveDataFormValues) => {
    try {
      await api.editVenueCollectiveData(venue.id, {
        ...values,
        collectiveDomains: values.collectiveDomains.map((stringId) =>
          Number(stringId)
        ),
        venueEducationalStatusId: values.collectiveLegalStatus
          ? Number(values.collectiveLegalStatus)
          : null,
      })

      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      navigate(
        `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif`
      )
    } catch {
      notify.error(SENT_DATA_ERROR_MESSAGE)
    }
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
                    description="Présenter la démarche d’éducation artistique et culturelle : présentation du lieu, actions menées auprès du public scolaire..."
                    maxLength={500}
                    isOptional
                  />
                </FormLayout.Row>

                <FormLayout.Row>
                  <SelectAutocomplete
                    multi
                    name="collectiveStudents"
                    label="Public cible"
                    options={studentOptions}
                    hideTags
                    isOptional
                  />
                </FormLayout.Row>

                <FormLayout.Row>
                  <TextInput
                    name="collectiveWebsite"
                    label="URL de votre site web"
                    description="Format : https://exemple.com"
                    isOptional
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>

              <FormLayout.SubSection
                title={
                  isOfferAddressEnabled
                    ? 'Informations de la structure'
                    : 'Informations du lieu'
                }
              >
                <FormLayout.Row>
                  <SelectAutocomplete
                    multi
                    hideTags
                    options={domains}
                    name="collectiveDomains"
                    label="Domaine artistique et culturel"
                    isOptional
                  />
                </FormLayout.Row>

                <FormLayout.Row>
                  <SelectAutocomplete
                    multi
                    hideTags
                    options={venueInterventionOptions}
                    name="collectiveInterventionArea"
                    label="Zone de mobilité"
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
                    isOptional
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
                    description="Format : email@exemple.com"
                    isOptional
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>
            </FormLayout.Section>
          </FormLayout>

          <div className={styles['action-bar']}>
            <ButtonLink
              variant={ButtonVariant.SECONDARY}
              to={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif`}
            >
              Annuler et quitter
            </ButtonLink>
            <Button type="submit" isLoading={formik.isSubmitting}>
              Enregistrer et quitter
            </Button>
          </div>
        </form>
      </FormikProvider>

      <RouteLeavingGuardVenueEdition
        shouldBlock={formik.dirty && !formik.isSubmitting}
      />
    </>
  )
}
