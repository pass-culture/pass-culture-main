import { useMemo } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import { useSignupJourneyContext } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { buildSelectOptions } from '@/commons/utils/buildSelectOptions'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { MultiSelect, type Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './ActivityForm.module.scss'

interface SocialUrl {
  url: string
}

export interface ActivityFormValues {
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType
  socialUrls: SocialUrl[]
  targetCustomer: {
    individual: boolean
    educational: boolean
  }
  phoneNumber: string
  culturalDomains: string[] | undefined
}

export const ActivityForm = (): JSX.Element => {
  const { data: educationalDomains, isLoading: isLoadingEducationalDomains } =
    useEducationalDomains()
  const { offerer } = useSignupJourneyContext()

  const { register, control, formState, watch, setValue, trigger, setFocus } =
    useFormContext<ActivityFormValues>()

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'socialUrls',
  })

  const watchSocialUrls = watch('socialUrls')

  const mainActivityOptions =
    offerer?.isOpenToPublic === 'true'
      ? buildSelectOptions(getActivities('OPEN_TO_PUBLIC'))
      : buildSelectOptions(getActivities('NOT_OPEN_TO_PUBLIC'))

  const defaultCulturalDomain: Option[] | undefined = useMemo(() => {
    return educationalDomains.length === 0 ||
      !formState.defaultValues ||
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
          {...register('activity')}
          error={formState.errors.activity?.message}
          label="Activité principale"
          className={styles['venue-type-select']}
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
            label="Domaine(s) d’activité"
            className={styles['cultural-domains-select']}
            required={offerer?.isOpenToPublic === 'false'}
            onSelectedOptionsChanged={(selectedOptions, _y, _z) => {
              setValue(
                'culturalDomains',
                selectedOptions.length > 0
                  ? selectedOptions.map((opt) => opt.label)
                  : undefined
              )
            }}
            buttonLabel={
              (watch('culturalDomains') ?? []).length > 0
                ? pluralizeFr(
                    (watch('culturalDomains') ?? []).length,
                    'domaine sélectionné',
                    'domaines sélectionnés'
                  )
                : 'Sélectionnez un ou plusieurs domaines d’activité'
            }
          />
        </FormLayout.Row>
      )}

      <FormLayout.Row mdSpaceAfter>
        <PhoneNumberInput
          {...register('phoneNumber')}
          error={formState.errors.phoneNumber?.message}
          label={'Téléphone (utilisé uniquement par le pass Culture)'}
          required
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
                      <Button
                        variant={ButtonVariant.SECONDARY}
                        color={ButtonColor.NEUTRAL}
                        icon={fullTrashIcon}
                        onClick={() => {
                          remove(index)
                          setFocus(`socialUrls.${index - 1}.url`)
                        }}
                        disabled={watchSocialUrls.length <= 1}
                        tooltip={'Supprimer l’url'}
                      />
                    </div>
                  )
                }
              />
            </div>
          </FormLayout.Row>
        ))}

        <Button
          variant={ButtonVariant.TERTIARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ url: '' })
          }}
          label="Ajouter un lien"
        />
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
