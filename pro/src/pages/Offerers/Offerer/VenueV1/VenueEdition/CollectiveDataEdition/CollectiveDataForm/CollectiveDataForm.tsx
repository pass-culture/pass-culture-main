import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  StudentLevels,
} from '@/apiClient/v1'
import {
  DEFAULT_MARSEILLE_STUDENTS,
  SENT_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import { offerInterventionOptions } from '@/commons/core/shared/interventionOptions'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { setSelectedPartnerVenue } from '@/commons/store/user/reducer'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { selectInterventionAreas } from '@/commons/utils/selectInterventionAreas'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullNextIcon from '@/icons/full-next.svg'
import { RouteLeavingGuardVenueEdition } from '@/pages/VenueEdition/components/RouteLeavingGuardVenueEdition'
import { DefinitionList } from '@/ui-kit/DefinitionList/DefinitionList'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './CollectiveDataForm.module.scss'
import type { CollectiveDataFormValues } from './type'
import { extractInitialValuesFromVenue } from './utils/extractInitialValuesFromVenue'
import { validationSchema } from './validationSchema'

type CollectiveDataFormProps = {
  statuses: SelectOption[]
}

const studentLevels = Object.entries(StudentLevels).map(([id, value]) => ({
  id,
  label: value,
}))

export const CollectiveDataForm = ({
  statuses,
}: Readonly<CollectiveDataFormProps>) => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const initialValues = extractInitialValuesFromVenue(selectedPartnerVenue)

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
      const updatedVenue = await api.editVenueCollectiveData(
        selectedPartnerVenue.id,
        {
          ...values,
          activity: values.activity as
            | ActivityOpenToPublic
            | ActivityNotOpenToPublic,
          collectiveDomains: values.collectiveDomains?.map(Number),
          collectiveLegalStatus: values.collectiveLegalStatus
            ? Number(values.collectiveLegalStatus)
            : null,
        }
      )

      dispatch(setSelectedPartnerVenue(updatedVenue))

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(`/partenaire/page-collective`)
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
              description="Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité."
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
              <DefinitionList>
                <DefinitionList.Row>
                  <DefinitionList.Term>Activité</DefinitionList.Term>
                  <DefinitionList.Definition>
                    {selectedPartnerVenue.activity
                      ? getActivityLabel(selectedPartnerVenue.activity)
                      : 'Non renseignée'}
                  </DefinitionList.Definition>
                </DefinitionList.Row>

                <DefinitionList.Row>
                  <DefinitionList.Term>
                    {pluralizeFr(
                      selectedPartnerVenue.collectiveDomains.length,
                      'Domaine artistique et culturel',
                      'Domaines artistiques et culturels'
                    )}
                  </DefinitionList.Term>
                  <DefinitionList.Definition>
                    {selectedPartnerVenue.collectiveDomains.length > 0
                      ? selectedPartnerVenue.collectiveDomains
                          .map((domain) => domain.name)
                          .join(', ')
                      : 'Non renseigné'}
                  </DefinitionList.Definition>
                </DefinitionList.Row>
              </DefinitionList>

              <Banner
                title="Les informations liées à votre activité se modifient dans la page Paramètres"
                actions={[
                  {
                    href: '/parametres/informations-generales',
                    icon: fullNextIcon,
                    label: 'Accéder à la page Paramètres',
                    type: 'link',
                  },
                ]}
              />

              <FormLayout.Row
                className={styles['collective-intervention-area-row']}
              >
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
            to={`/partenaire/page-collective`}
            label="Annuler"
          />

          <Button type="submit" isLoading={isSubmitting} label="Enregistrer" />
        </div>
      </form>

      <RouteLeavingGuardVenueEdition shouldBlock={isDirty && !isSubmitting} />
    </>
  )
}
