import { FormikProvider, useFormik } from 'formik'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { GetVenueResponseModel, StudentLevels } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import FormLayout from 'components/FormLayout'
import { handleAllFranceDepartmentOptions } from 'core/shared'
import { venueInterventionOptions } from 'core/shared/interventionOptions'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { RouteLeavingGuardVenueEdition } from 'pages/VenueEdition/RouteLeavingGuardVenueEdition'
import { GET_VENUE_QUERY_KEY } from 'pages/VenueEdition/VenueEdition'
import { ButtonLink, Select, SubmitButton, TextArea, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { MultiSelectAutocomplete } from 'ui-kit/form/MultiSelectAutoComplete/MultiSelectAutocomplete'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import editVenueCollectiveDataAdapter from '../adapters/editVenueCollectiveDataAdapter'

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
}

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
  const [isLoading, setIsLoading] = useState(false)
  const initialValues = extractInitialValuesFromVenue(venue)

  const onSubmit = async (values: CollectiveDataFormValues) => {
    setIsLoading(true)
    const response = await editVenueCollectiveDataAdapter({
      venueId: venue.id,
      values,
    })

    if (!response.isOk) {
      notify.error(response.message)
      return setIsLoading(false)
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
                    : 'Cet espace vous permet de présenter votre activité culturelle aux utilisateurs de l’application pass Culture. Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité.'
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

          <ActionsBarSticky>
            <ActionsBarSticky.Left>
              <ButtonLink
                variant={ButtonVariant.SECONDARY}
                link={{
                  isExternal: false,
                  to: `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/eac`,
                }}
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

      <RouteLeavingGuardVenueEdition
        shouldBlock={formik.dirty && !formik.isSubmitting}
      />
    </>
  )
}
