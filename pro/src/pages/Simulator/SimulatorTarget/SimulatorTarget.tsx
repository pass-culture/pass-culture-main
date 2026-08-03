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
  saveTargetAudienceToStorage,
  tryRestoreTargetAudienceFromStorage,
} from '../storage'
import styles from './SimulatorTarget.module.scss'
import {
  type SimulatorTargetAudienceFormValues,
  validationSchema,
} from './validationSchema'

const defaultFormValues = {
  targetAudiences: {
    individual: false,
    collective: false,
  },
}

export const SimulatorTarget = (): JSX.Element => {
  const navigate = useNavigate()
  const { targetAudiences, setTargetAudiences } = useSimulatorContext()

  const { formState, reset, watch, setValue, trigger, handleSubmit } = useForm({
    defaultValues: targetAudiences
      ? {
          targetAudiences: {
            individual: targetAudiences.individual ?? false,
            collective: targetAudiences.collective ?? false,
          },
        }
      : defaultFormValues,
    resolver: yupResolver(validationSchema),
  })

  useEffect(() => {
    try {
      const targetAudienceStoredData =
        tryRestoreTargetAudienceFromStorage(setTargetAudiences)
      if (targetAudienceStoredData) {
        reset({ targetAudiences: targetAudienceStoredData })
      }
    } catch {
      // Nothing to do
    }
  }, [setTargetAudiences, reset])

  const onSubmit = (formValues: SimulatorTargetAudienceFormValues) => {
    saveTargetAudienceToStorage(formValues.targetAudiences)
    setTargetAudiences(formValues.targetAudiences)
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
                    checked: watch('targetAudiences.individual') ?? false,
                    onChange: async (e) => {
                      setValue('targetAudiences.individual', e.target.checked)
                      await trigger('targetAudiences')
                    },
                  },
                  {
                    label: 'Les groupes scolaires via ADAGE',
                    sizing: 'fill',
                    checked: watch('targetAudiences.collective') ?? false,
                    onChange: async (e) => {
                      setValue('targetAudiences.collective', e.target.checked)
                      await trigger('targetAudiences')
                    },
                  },
                ]}
                variant="detailed"
                error={formState.errors.targetAudiences?.message}
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
                page={4}
                total={4}
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
