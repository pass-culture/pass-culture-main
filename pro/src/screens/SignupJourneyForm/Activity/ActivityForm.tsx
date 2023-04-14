import cn from 'classnames'
import { FieldArray, useFormikContext } from 'formik'
import React from 'react'

import { VenueTypeCode } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { PlusCircleIcon, TrashFilledIcon } from 'icons'
import { Button, CheckboxGroup, Select, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './ActivityForm.module.scss'
import { activityTargetCustomerCheckboxGroup } from './constants'

export interface IActivityFormValues {
  venueTypeCode: VenueTypeCode | ''
  socialUrls: string[]
  targetCustomer: {
    individual: boolean
    educational: boolean
  }
}

export interface IActivityFormProps {
  venueTypes: SelectOption[]
}

const ActivityForm = ({ venueTypes }: IActivityFormProps): JSX.Element => {
  const { values } = useFormikContext<IActivityFormValues>()

  return (
    <FormLayout.Section
      title="Activité"
      className={styles['activity-form-wrapper']}
    >
      <FormLayout.Row>
        <Select
          options={[
            {
              value: '',
              label: 'Sélectionnez votre activité principale',
            },
            ...venueTypes,
          ]}
          name="venueTypeCode"
          label="Activité principale"
          className={styles['venue-type-select']}
        />
      </FormLayout.Row>
      <FieldArray
        name="socialUrls"
        render={arrayHelpers => (
          <FormLayout.Row>
            {values.socialUrls.map((url, index) => (
              <FormLayout.Row key={index} inline>
                <TextInput
                  name={`socialUrls[${index}]`}
                  label="Site internet, réseau social"
                  placeholder="https://www.siteinternet.com"
                  type="url"
                  className={styles['url-input']}
                  isLabelHidden={index !== 0}
                  isOptional
                />

                <div
                  className={cn(styles['form-row-actions'], {
                    [styles['first-row']]: index === 0,
                  })}
                >
                  <Button
                    variant={ButtonVariant.TERNARY}
                    Icon={TrashFilledIcon}
                    iconPosition={IconPositionEnum.CENTER}
                    disabled={values.socialUrls.length <= 1}
                    onClick={() => arrayHelpers.remove(index)}
                    className={styles['delete-button']}
                    hasTooltip
                  >
                    Supprimer l'url
                  </Button>
                </div>
              </FormLayout.Row>
            ))}

            <Button
              variant={ButtonVariant.TERNARY}
              Icon={PlusCircleIcon}
              onClick={() => {
                arrayHelpers.push('')
              }}
            >
              Ajouter un lien
            </Button>
          </FormLayout.Row>
        )}
      />
      <FormLayout.Row>
        <CheckboxGroup
          group={activityTargetCustomerCheckboxGroup}
          groupName="targetCustomer"
          legend="À qui souhaitez-vous destiner vos offres sur le pass Culture ? Cette information est collectée à titre informatif."
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ActivityForm
