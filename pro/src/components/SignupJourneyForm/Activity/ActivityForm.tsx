import { useFieldArray, useFormContext } from 'react-hook-form'

import type { VenueTypeResponseModel } from '@/apiClient/v1'
import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getActivities } from '@/commons/mappings/mappings'
import { buildSelectOptions } from '@/commons/utils/buildSelectOptions'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import styles from './ActivityForm.module.scss'

interface SocialUrl {
  url: string
}
export interface ActivityFormValues {
  venueTypeCode: string
  socialUrls: SocialUrl[]
  targetCustomer: {
    individual: boolean
    educational: boolean
  }
  phoneNumber: string
}

export interface ActivityFormProps {
  venueTypes: VenueTypeResponseModel[]
}

export const ActivityForm = ({
  venueTypes,
}: ActivityFormProps): JSX.Element => {
  const { offerer } = useSignupJourneyContext()

  const { register, control, formState, watch, setValue, trigger, setFocus } =
    useFormContext<ActivityFormValues>()

  const isVenueActivityFeatureActive = useActiveFeature('WIP_VENUE_ACTIVITY')

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'socialUrls',
  })

  const watchSocialUrls = watch('socialUrls')

  const mainActivityOptions =
    isVenueActivityFeatureActive && offerer?.isOpenToPublic === 'true'
      ? buildSelectOptions(getActivities())
      : venueTypes
  return (
    <FormLayout.Section>
      <FormLayout.Row mdSpaceAfter>
        <Select
          options={[
            {
              value: '',
              label: 'Sélectionnez votre activité principale',
            },
            ...mainActivityOptions,
          ]}
          {...register('venueTypeCode')}
          error={formState.errors.venueTypeCode?.message}
          label="Activité principale"
          className={styles['venue-type-select']}
          required
          requiredIndicator="explicit"
        />
      </FormLayout.Row>

      <FormLayout.Row mdSpaceAfter>
        <PhoneNumberInput
          {...register('phoneNumber')}
          error={formState.errors.phoneNumber?.message}
          label={'Téléphone (utilisé uniquement par le pass Culture)'}
          required
          requiredIndicator="explicit"
        />
      </FormLayout.Row>

      <FormLayout.Row mdSpaceAfter className={styles['url-list']}>
        {fields.map((field, index) => (
          <FormLayout.Row key={field.id}>
            <div className={styles['url-input']}>
              <TextInput
                {...register(`socialUrls.${index}.url`)}
                label="Site internet, réseau social"
                description="Format : https://www.siteinternet.com"
                type="url"
                error={formState.errors.socialUrls?.[index]?.url?.message}
                extension={
                  watchSocialUrls.length > 1 && (
                    <div
                      data-error={
                        formState.errors.socialUrls?.[index] ? 'true' : 'false'
                      }
                    >
                      <ListIconButton
                        icon={fullTrashIcon}
                        onClick={() => {
                          remove(index)
                          setFocus(`socialUrls.${index - 1}.url`)
                        }}
                        disabled={watchSocialUrls.length <= 1}
                        className={styles['delete-button']}
                        tooltipContent={<>Supprimer l’url</>}
                      />
                    </div>
                  )
                }
              />
            </div>
          </FormLayout.Row>
        ))}

        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ url: '' })
          }}
        >
          Ajouter un lien
        </Button>
      </FormLayout.Row>

      <FormLayout.Row className={styles['target-customer-row']}>
        <CheckboxGroup
          label="À qui souhaitez-vous destiner vos offres sur le pass Culture ? Cette information est collectée à titre informatif."
          description="Sélectionnez au moins une option"
          options={[
            {
              label: 'Au grand public',
              sizing: 'fill',
              checked: watch('targetCustomer.individual'),
              onChange: async (e) => {
                setValue('targetCustomer.individual', e.target.checked)
                await trigger('targetCustomer')
              },
            },
            {
              label: 'À des groupes scolaires',
              sizing: 'fill',
              checked: watch('targetCustomer.educational'),
              onChange: async (e) => {
                setValue('targetCustomer.educational', e.target.checked)
                await trigger('targetCustomer')
              },
            },
          ]}
          variant="detailed"
          error={formState.errors.targetCustomer?.message}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
