import { FieldArray, useFormikContext } from 'formik'
import { useRef } from 'react'

import { VenueTypeResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { buildVenueTypesOptions } from 'pages/VenueEdition/buildVenueTypesOptions'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import styles from './ActivityForm.module.scss'

export interface ActivityFormValues {
  venueTypeCode: string
  socialUrls: string[]
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
  const { values, errors, setFieldValue, getFieldMeta } =
    useFormikContext<ActivityFormValues>()
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  return (
    <FormLayout.Section>
      <h1 className={styles['activity-form-wrapper']}>Activité</h1>
      <FormLayout.Row>
        <Select
          options={[
            {
              value: '',
              label: 'Sélectionnez votre activité principale',
            },
            ...venueTypesOptions,
          ]}
          name="venueTypeCode"
          label="Activité principale"
          className={styles['venue-type-select']}
        />
      </FormLayout.Row>
      {isNewSignupEnabled && (
        <FormLayout.Row>
          <PhoneNumberInput
            name="phoneNumber"
            label={'Téléphone (utilisé uniquement par le pass Culture)'}
          />
        </FormLayout.Row>
      )}
      <FieldArray
        name="socialUrls"
        render={(arrayHelpers) => (
          <FormLayout.Row>
            {values.socialUrls.map((_url, index) => (
              <FormLayout.Row key={index}>
                <TextInput
                  name={`socialUrls[${index}]`}
                  label="Site internet, réseau social"
                  description="Format : https://www.siteinternet.com"
                  data-testid="activity-form-social-url"
                  type="url"
                  className={styles['url-input']}
                  isLabelHidden={index !== 0}
                  isOptional
                  focusRef={(el) => {
                    inputRefs.current[index] = el
                  }}
                  InputExtension={
                    <div
                      data-error={errors.socialUrls?.[index] ? 'true' : 'false'}
                    >
                      <ListIconButton
                        icon={fullTrashIcon}
                        onClick={() => {
                          const newIndex = index - 1
                          inputRefs.current[newIndex]?.focus()

                          arrayHelpers.remove(index)
                        }}
                        disabled={values.socialUrls.length <= 1}
                        className={styles['delete-button']}
                        tooltipContent={<>Supprimer l’url</>}
                      />
                    </div>
                  }
                />
              </FormLayout.Row>
            ))}

            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullMoreIcon}
              onClick={() => {
                arrayHelpers.push('')
                // Focus on the newly added input after it has been rendered
                setTimeout(() => {
                  const lastInput = document.querySelector(
                    `input[name="socialUrls[${values.socialUrls.length}]"]`
                  ) as HTMLInputElement
                  lastInput.focus()
                }, 0)
              }}
            >
              Ajouter un lien
            </Button>
          </FormLayout.Row>
        )}
      />
      <FormLayout.Row className={styles['target-customer-row']}>
        <CheckboxGroup
          group={[
            {
              label: 'Au grand public',
              checked: values.targetCustomer.individual,
              sizing: 'fill',
              onChange: (e) =>
                setFieldValue('targetCustomer.individual', e.target.checked),
            },
            {
              label: 'À des groupes scolaires',
              checked: values.targetCustomer.educational,
              sizing: 'fill',
              onChange: (e) =>
                setFieldValue('targetCustomer.educational', e.target.checked),
            },
          ]}
          name="targetCustomer"
          legend="À qui souhaitez-vous destiner vos offres sur le pass Culture ? Cette information est collectée à titre informatif."
          error={getFieldMeta('targetCustomer').error}
          required
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
