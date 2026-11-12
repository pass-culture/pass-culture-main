import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { TargetAudience } from '@/apiClient/v1'
import { claimNavigationFocus } from '@/app/App/hook/useFocus'
import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
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

const audiencesToFormValues = (
  audiences: TargetAudience[] | null | undefined
): SimulatorTargetAudienceFormValues['targetAudiences'] => ({
  individual: audiences?.includes(TargetAudience.INDIVIDUAL) ?? false,
  collective: audiences?.includes(TargetAudience.COLLECTIVE) ?? false,
})

const formValuesToAudiences = (
  values: SimulatorTargetAudienceFormValues['targetAudiences']
): TargetAudience[] => [
  ...(values.individual ? [TargetAudience.INDIVIDUAL] : []),
  ...(values.collective ? [TargetAudience.COLLECTIVE] : []),
]

export const SimulatorTarget = (): JSX.Element => {
  const navigate = useNavigate()
  const { targetAudiences, setTargetAudiences } = useSimulatorContext()
  const titleRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    claimNavigationFocus(titleRef.current)
  }, [])

  const methods = useForm({
    defaultValues: targetAudiences
      ? { targetAudiences: audiencesToFormValues(targetAudiences) }
      : defaultFormValues,
    resolver: yupResolver(validationSchema),
  })
  const { formState, reset, watch, setValue, trigger, handleSubmit } = methods

  useEffect(() => {
    try {
      const targetAudienceStoredData =
        tryRestoreTargetAudienceFromStorage(setTargetAudiences)
      if (targetAudienceStoredData) {
        reset({
          targetAudiences: audiencesToFormValues(targetAudienceStoredData),
        })
      }
    } catch {
      // Nothing to do
    }
  }, [setTargetAudiences, reset])

  const onSubmit = (formValues: SimulatorTargetAudienceFormValues) => {
    const audiences = formValuesToAudiences(formValues.targetAudiences)
    saveTargetAudienceToStorage(audiences)
    setTargetAudiences(audiences)
    void navigate('/inscription/preparation/resultats')
  }

  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={styles['title']} ref={titleRef} tabIndex={-1}>
          Quels publics souhaitez-vous cibler ?
        </h1>
        <p className={commonStyles['subtitle']}>
          Selon votre réponse, nous vous orienterons vers le bon dispositif
          d'inscription.
        </p>
      </div>

      <FormLayout>
        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <ScrollToFirstHookFormErrorAfterSubmit />
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
                  as="router-link"
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
        </FormProvider>
      </FormLayout>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorTarget
