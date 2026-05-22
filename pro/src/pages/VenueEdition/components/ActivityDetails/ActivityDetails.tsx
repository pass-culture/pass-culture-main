import { useMemo } from 'react'
import { useFormContext } from 'react-hook-form'

import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { buildSelectOptions } from '@/commons/utils/buildSelectOptions'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MultiSelect, type Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './ActivityDetails.module.scss'

interface ActivityFormFields {
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
  isOpenToPublic: string
  culturalDomains?: string[]
  description?: string
}

interface ActivityDetailsProps {
  isVenueVirtual: boolean
}

export const ActivityDetails = ({ isVenueVirtual }: ActivityDetailsProps) => {
  const { register, watch, setValue, formState } =
    useFormContext<ActivityFormFields>()
  const { data: educationalDomains, isLoading: isLoadingEducationalDomains } =
    useEducationalDomains()

  const defaultCulturalDomain: Option[] | undefined = useMemo(() => {
    return educationalDomains.length === 0 ||
      !formState.defaultValues?.culturalDomains
      ? undefined
      : educationalDomains
          .filter((apiDomain) =>
            formState.defaultValues?.culturalDomains?.find(
              (domain) => apiDomain.name === domain
            )
          )
          .map((domain) => {
            return { id: String(domain.id), label: domain.name }
          })
  }, [educationalDomains, formState.defaultValues])

  return (
    <FormLayout.SubSection title="À propos de votre activité">
      <FormLayout.Row key={watch('activity')} mdSpaceAfter>
        <Select
          {...register('activity')}
          options={[
            ...(watch('activity') === null // TODO: make `activity` not nullable after migrating all the venues with VenueTypeCode and no matching activity
              ? [
                  {
                    value: '',
                    label: 'Sélectionnez votre activité principale',
                  },
                ]
              : []),
            ...buildSelectOptions(
              getActivities(
                watch('isOpenToPublic') === 'true'
                  ? 'OPEN_TO_PUBLIC'
                  : 'NOT_OPEN_TO_PUBLIC'
              )
            ),
          ]}
          label="Activité principale"
          disabled={isVenueVirtual}
          error={formState.errors.activity?.message}
          required
        />
      </FormLayout.Row>
      {!isLoadingEducationalDomains && (
        <FormLayout.Row mdSpaceAfter>
          <MultiSelect
            name="culturalDomains"
            options={educationalDomains.map((educationalDomain) => ({
              id: String(educationalDomain.id),
              label: educationalDomain.name,
            }))}
            defaultOptions={defaultCulturalDomain}
            error={formState.errors.culturalDomains?.message}
            label="Domaine(s) d'activité"
            required={watch('isOpenToPublic') === 'false'}
            onSelectedOptionsChanged={(selectedOptions) => {
              setValue(
                'culturalDomains',
                selectedOptions.map((opt) => opt.label),
                { shouldDirty: true }
              )
            }}
            buttonLabel={
              (watch('culturalDomains') ?? []).length > 0
                ? pluralizeFr(
                    (watch('culturalDomains') ?? []).length,
                    'domaine sélectionné',
                    'domaines sélectionnés'
                  )
                : "Sélectionnez un ou plusieurs domaines d'activité"
            }
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        {!isVenueVirtual && (
          <p className={styles['description-helper']}>
            Vous pouvez décrire les différentes actions que vous menez, votre
            histoire ou préciser des informations sur votre activité.
          </p>
        )}
        <TextArea
          label="Description"
          description="Par exemple : mon établissement propose des spectacles, de l'improvisation..."
          maxLength={1000}
          {...register('description')}
          error={formState.errors.description?.message}
        />
      </FormLayout.Row>
    </FormLayout.SubSection>
  )
}
