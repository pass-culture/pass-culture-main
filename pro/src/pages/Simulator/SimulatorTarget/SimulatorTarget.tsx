import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

import { useSimulatorContext } from '../SimulatorContext'
import {
  saveTargetCustomerToStorage,
  tryRestoreTargetCustomerFromStorage,
} from '../storage'
import styles from './SimulatorTarget.module.scss'
import {
  type SimulatorTargetCustomerFormValues,
  validationSchema,
} from './validationSchema'

const defaultFormValues = {
  targetCustomer: {
    individual: false,
    educational: false,
  },
}

export const SimulatorTarget = (): JSX.Element => {
  const navigate = useNavigate()
  const { targetCustomer, setTargetCustomer } = useSimulatorContext()

  const { formState, reset, watch, setValue, trigger, handleSubmit } = useForm({
    defaultValues: targetCustomer
      ? {
          targetCustomer: {
            individual: targetCustomer.individual ?? false,
            educational: targetCustomer.educational ?? false,
          },
        }
      : defaultFormValues,
    resolver: yupResolver(validationSchema),
  })

  useEffect(() => {
    try {
      const targetCustomerStoredData =
        tryRestoreTargetCustomerFromStorage(setTargetCustomer)
      if (targetCustomerStoredData) {
        reset({ targetCustomer: targetCustomerStoredData })
      }
    } catch {
      // Nothing to do
    }
  }, [setTargetCustomer, reset])

  const onSubmit = (formValues: SimulatorTargetCustomerFormValues) => {
    saveTargetCustomerToStorage(formValues.targetCustomer)
    setTargetCustomer(formValues.targetCustomer)
    navigate('/inscription/preparation/resultats')
  }

  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quels publics souhaitez-vous cibler ?
        </h1>
        <p className={commonStyles['subtitle']}>
          Selon votre réponse, nous vous orienterons vers le bon dispositif
          d'inscription.
        </p>
      </div>

      <FormLayout>
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormLayout.Section>
            <FormLayout.Row className={styles['row-field-public']}>
              <CheckboxGroup
                label="Public cibles"
                description="Sélectionnez au moins une option"
                options={[
                  {
                    label: 'Les jeunes via l’application pass Culture',
                    sizing: 'fill',
                    checked: watch('targetCustomer.individual') ?? false,
                    onChange: async (e) => {
                      setValue('targetCustomer.individual', e.target.checked)
                      await trigger('targetCustomer')
                    },
                  },
                  {
                    label: 'Les groupes scolaires via ADAGE',
                    sizing: 'fill',
                    checked: watch('targetCustomer.educational') ?? false,
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

            <div className={commonStyles['action-bar']}>
              <Button
                as="a"
                to="/inscription/preparation/activite"
                variant={ButtonVariant.SECONDARY}
                label="Retour"
              />
              <BubbleStepper
                page={3}
                total={3}
                className={commonStyles['action-bar-stepper']}
              />
              <Button type="submit" label="Continuer" />
            </div>
          </FormLayout.Section>
        </form>
      </FormLayout>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorTarget
