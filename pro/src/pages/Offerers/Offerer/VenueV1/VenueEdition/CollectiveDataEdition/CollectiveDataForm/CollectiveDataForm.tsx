import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { type GetVenueResponseModel, StudentLevels } from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  DEFAULT_MARSEILLE_STUDENTS,
  SENT_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { offerInterventionOptions } from '@/commons/core/shared/interventionOptions'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { selectInterventionAreas } from '@/commons/utils/selectInterventionAreas'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { RouteLeavingGuardVenueEdition } from '@/pages/VenueEdition/components/RouteLeavingGuardVenueEdition'
import { MultiSelect, type Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './CollectiveDataForm.module.scss'
import type { CollectiveDataFormValues } from './type'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { validationSchema } from './validationSchema'

type CollectiveDataFormProps = {
  statuses: SelectOption[]
  domains: Option[]
  venue: GetVenueResponseModel
}

const studentLevels = Object.entries(StudentLevels).map(([id, value]) => ({
  id,
  label: value,
}))

export const CollectiveDataForm = ({
  statuses,
  domains,
  venue,
}: CollectiveDataFormProps): JSX.Element | null => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()

  const initialValues = extractInitialValuesFromVenue(venue)

  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const studentOptions = isMarseilleEnabled
    ? studentLevels
    : studentLevels.filter(
        (level) => !DEFAULT_MARSEILLE_STUDENTS.includes(level.label)
      )

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<CollectiveDataFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<CollectiveDataFormValues, unknown, unknown>(
      validationSchema
    ),
    mode: 'onBlur',
  })

  const onSubmit = async (values: CollectiveDataFormValues): Promise<void> => {
    try {
      await api.editVenueCollectiveData(venue.id, {
        ...values,
        collectiveDomains: values.collectiveDomains?.map(Number),
        venueEducationalStatusId: values.collectiveLegalStatus
          ? Number(values.collectiveLegalStatus)
          : null,
      })

      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif`
      )
    } catch {
      snackBar.error(SENT_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)}>
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
                  label="Démarche d’éducation artistique et culturelle"
                  description="Présenter la démarche d’éducation artistique et culturelle : présentation du lieu, actions menées auprès du public scolaire..."
                  maxLength={500}
                  {...register('collectiveDescription')}
                  error={errors.collectiveDescription?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <MultiSelect
                  name="collectiveStudents"
                  label="Public cible"
                  options={studentOptions}
                  defaultOptions={studentOptions.filter((option) =>
                    watch('collectiveStudents')?.includes(option.label)
                  )}
                  hasSearch
                  searchLabel="Rechercher un public cible"
                  buttonLabel="Public cible"
                  onSelectedOptionsChanged={(selectedOptions) => {
                    setValue(
                      'collectiveStudents',
                      selectedOptions.map((opt) => opt.label as StudentLevels)
                    )
                  }}
                  error={errors.collectiveStudents?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="URL de votre site web"
                  type="url"
                  description="Format : https://exemple.com"
                  {...register('collectiveWebsite')}
                  error={errors.collectiveWebsite?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>

            <FormLayout.SubSection title="Informations de la structure">
              <FormLayout.Row>
                <MultiSelect
                  name="collectiveDomains"
                  label="Domaine artistique et culturel"
                  options={domains}
                  defaultOptions={domains.filter((option) =>
                    watch('collectiveDomains')?.includes(option.id)
                  )}
                  hasSearch
                  searchLabel="Rechercher un domaine artistique et culturel"
                  buttonLabel="Domaines artistiques"
                  onSelectedOptionsChanged={(selectedOptions) =>
                    setValue(
                      'collectiveDomains',
                      selectedOptions.map((opt) => opt.id)
                    )
                  }
                  error={errors.collectiveDomains?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <MultiSelect
                  name="collectiveInterventionArea"
                  label="Zone de mobilité"
                  options={offerInterventionOptions}
                  selectedOptions={offerInterventionOptions.filter((op) =>
                    watch('collectiveInterventionArea')?.includes(op.id)
                  )}
                  hasSelectAllOptions
                  hasSearch
                  searchLabel="Rechercher une zone de mobilité"
                  buttonLabel="Département(s)"
                  onSelectedOptionsChanged={(
                    selectedOptions,
                    added,
                    removed
                  ) => {
                    const updated = selectInterventionAreas({
                      selectedOption: selectedOptions,
                      addedOptions: added,
                      removedOptions: removed,
                    })

                    setValue('collectiveInterventionArea', Array.from(updated))
                  }}
                  error={errors.collectiveInterventionArea?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <Select
                  label="Statut"
                  {...register('collectiveLegalStatus')}
                  options={[
                    { value: '', label: 'Sélectionner un statut' },
                    ...statuses,
                  ]}
                  error={errors.collectiveLegalStatus?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>

            <FormLayout.SubSection title="Contact">
              <FormLayout.Row mdSpaceAfter>
                <PhoneNumberInput
                  label="Téléphone"
                  {...register('collectivePhone')}
                  error={errors.collectivePhone?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <TextInput
                  label="Email"
                  type="email"
                  description="Format : email@exemple.com"
                  {...register('collectiveEmail')}
                  error={errors.collectiveEmail?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <div className={styles['action-bar']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            to={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/collectif`}
            label="Annuler"
          />

          <Button type="submit" isLoading={isSubmitting} label="Enregistrer" />
        </div>
      </form>

      <RouteLeavingGuardVenueEdition shouldBlock={isDirty && !isSubmitting} />
    </>
  )
}
