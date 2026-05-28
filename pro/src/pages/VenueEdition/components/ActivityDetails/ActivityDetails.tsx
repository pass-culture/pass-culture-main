import { useFormContext } from 'react-hook-form'

import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { buildSelectOptions } from '@/commons/utils/buildSelectOptions'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { Select } from '@/ui-kit/form/Select/Select'

import { defaultCulturalDomain } from './activityDomainsHelper'

interface ActivityFormFields {
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
  isOpenToPublic: string
  culturalDomains?: string[]
  description?: string
}

export const ActivityDetails = () => {
  const { register, watch, setValue, formState } =
    useFormContext<ActivityFormFields>()

  const { data: educationalDomains, isLoading: isLoadingEducationalDomains } =
    useEducationalDomains()

  const defaultCulturalDomains = defaultCulturalDomain(
    formState,
    educationalDomains
  )

  return (
    <>
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
            defaultOptions={defaultCulturalDomains}
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
    </>
  )
}
