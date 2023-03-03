import cn from 'classnames'
import { FieldArray, useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { PlusCircleIcon, TrashFilledIcon } from 'icons'
import { Button, RadioGroup, Select, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './ActivityForm.module.scss'
import {
  activityTargetCustomerTypeRadios,
  TargetCustomerTypeEnum,
} from './constants'

export interface IActivityFormValues {
  venueType: string
  socialUrls: string[]
  targetCustomer: TargetCustomerTypeEnum | undefined | null
}

export interface IActivityFormProps {
  venueTypes: SelectOption[]
}

const ActivityForm = ({ venueTypes }: IActivityFormProps): JSX.Element => {
  const { values } = useFormikContext<IActivityFormValues>()

  return (
    <FormLayout.Section title="Activité">
      <FormLayout.MandatoryInfo />
      <FormLayout.Row>
        <Select
          options={[
            {
              value: '',
              label: 'Sélectionnez votre activité principale',
            },
            ...venueTypes,
          ]}
          name="venueType"
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
              Ajouter une url
            </Button>
          </FormLayout.Row>
        )}
      />
      <FormLayout.Row>
        <RadioGroup
          group={activityTargetCustomerTypeRadios}
          legend="A qui souhaitez-vous proposer vos offres ?"
          name="targetCustomer"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ActivityForm
