import cn from 'classnames'
import { FieldArray, useFormikContext } from 'formik'
import React from 'react'

import { VenueTypeResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { buildVenueTypesOptions } from 'pages/VenueCreation/buildVenueTypesOptions'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { Select } from 'ui-kit/form/Select/Select'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import styles from './ActivityForm.module.scss'
import { activityTargetCustomerCheckboxGroup } from './constants'

export interface ActivityFormValues {
  venueTypeCode: string
  socialUrls: string[]
  targetCustomer: {
    individual: boolean
    educational: boolean
  }
}

export interface ActivityFormProps {
  venueTypes: VenueTypeResponseModel[]
}

export const ActivityForm = ({
  venueTypes,
}: ActivityFormProps): JSX.Element => {
  const { values } = useFormikContext<ActivityFormValues>()
  const venueTypesOptions = buildVenueTypesOptions(venueTypes)

  return (
    <FormLayout.Section>
      <h1 className={styles['activity-form-wrapper']}>Activité</h1>
      <FormLayout.Row className={styles['input-gap']}>
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
      <FieldArray
        name="socialUrls"
        render={(arrayHelpers) => (
          <FormLayout.Row>
            {values.socialUrls.map((url, index) => (
              <FormLayout.Row key={index} className={styles['input-gap']}>
                <TextInput
                  name={`socialUrls[${index}]`}
                  label="Site internet, réseau social"
                  placeholder="https://www.siteinternet.com"
                  data-testid="activity-form-social-url"
                  type="url"
                  className={styles['url-input']}
                  isLabelHidden={index !== 0}
                  isOptional
                />

                <div
                  className={cn(styles['form-row-actions'], {
                    [styles['first-row'] ?? '']: index === 0,
                  })}
                >
                  <ListIconButton
                    icon={fullTrashIcon}
                    onClick={() => arrayHelpers.remove(index)}
                    disabled={values.socialUrls.length <= 1}
                    className={styles['delete-button']}
                  >
                    Supprimer l’url
                  </ListIconButton>
                </div>
              </FormLayout.Row>
            ))}

            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullMoreIcon}
              onClick={() => {
                arrayHelpers.push('')
              }}
            >
              Ajouter un lien
            </Button>
          </FormLayout.Row>
        )}
      />
      <FormLayout.Row className={styles['target-customer-row']}>
        <CheckboxGroup
          group={activityTargetCustomerCheckboxGroup}
          groupName="targetCustomer"
          legend="À qui souhaitez-vous destiner vos offres sur le pass Culture ? Cette information est collectée à titre informatif."
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
