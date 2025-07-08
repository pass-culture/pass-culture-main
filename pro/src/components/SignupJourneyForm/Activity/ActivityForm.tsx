import { useRef } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import { VenueTypeResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { buildVenueTypesOptions } from 'pages/VenueEdition/buildVenueTypesOptions'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

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
  phoneNumber: string | undefined
}

export interface ActivityFormProps {
  venueTypes: VenueTypeResponseModel[]
}

export const ActivityForm = ({
  venueTypes,
}: ActivityFormProps): JSX.Element => {
  const { register, control, formState, watch, setValue, trigger } =
    useFormContext<ActivityFormValues>()

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'socialUrls',
  })

  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)
  const watchSocialUrls = watch('socialUrls')

  return (
    <FormLayout.Section>
      <h1 className={styles['activity-form-wrapper']}>Activité</h1>
      <FormLayout.Row mdSpaceAfter>
        <Select
          options={[
            {
              value: '',
              label: 'Sélectionnez votre activité principale',
            },
            ...venueTypesOptions,
          ]}
          {...register('venueTypeCode')}
          error={formState.errors.venueTypeCode?.message}
          label="Activité principale"
          className={styles['venue-type-select']}
          required
        />
      </FormLayout.Row>

      {isNewSignupEnabled && (
        <FormLayout.Row>
          <PhoneNumberInput
            {...register('phoneNumber')}
            error={formState.errors.phoneNumber?.message}
            label={'Téléphone (utilisé uniquement par le pass Culture)'}
            required
          />
        </FormLayout.Row>
      )}

      <FormLayout.Row mdSpaceAfter>
        {fields.map((field, index) => (
          <FormLayout.Row key={field.id}>
            <TextInput
              {...register(`socialUrls.${index}.url`)}
              label="Site internet, réseau social"
              description="Format : https://www.siteinternet.com"
              data-testid="activity-form-social-url"
              type="url"
              className={styles['url-input']}
              isLabelHidden={index !== 0}
              error={formState.errors.socialUrls?.[index]?.url?.message}
              InputExtension={
                watchSocialUrls.length > 1 && (
                  <div
                    data-error={
                      formState.errors.socialUrls?.[index] ? 'true' : 'false'
                    }
                  >
                    <ListIconButton
                      icon={fullTrashIcon}
                      onClick={() => {
                        const newIndex = index - 1
                        inputRefs.current[newIndex]?.focus()
                        remove(index)
                      }}
                      disabled={watchSocialUrls.length <= 1}
                      className={styles['delete-button']}
                      tooltipContent={<>Supprimer l’url</>}
                    />
                  </div>
                )
              }
            />
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
          name="targetCustomer"
          group={[
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
          legend="À qui souhaitez-vous destiner vos offres sur le pass Culture ? Cette information est collectée à titre informatif."
          error={formState.errors.targetCustomer?.message}
          required
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
