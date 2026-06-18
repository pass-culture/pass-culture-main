import { yupResolver } from '@hookform/resolvers/yup'
import { activityValidator } from 'commons/utils/yup/activity'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useSimulatorContext } from 'pages/Simulator/SimulatorContext'
import {
  saveActivityToStorage,
  tryRestoreActivityFromStorage,
} from 'pages/Simulator/storage'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import { Select } from 'ui-kit/form/Select/Select'
import * as yup from 'yup'

import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { ActivityNotOpenToPublicMap } from '@/commons/mappings/ActivityNotOpenToPublic'
import { ActivityOpenToPublicMap } from '@/commons/mappings/ActivityOpenToPublic'
import { toSelectOptions } from '@/commons/mappings/helpers'
import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

export interface SimulatorActivity {
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic
}

export const SimulatorActivity = (): JSX.Element => {
  const { activity, setActivity, openToPublic } = useSimulatorContext()
  const navigate = useNavigate()

  const mainActivityOptions =
    openToPublic === 'true'
      ? toSelectOptions(ActivityOpenToPublicMap)
      : toSelectOptions(ActivityNotOpenToPublicMap)

  const methods = useForm<SimulatorActivity>({
    defaultValues: { activity: activity },
    resolver: yupResolver<SimulatorActivity, unknown, unknown>(
      yup.object().shape({
        activity: activityValidator(openToPublic !== 'true').required(
          'Veuillez sélectionner une activité principale'
        ),
      })
    ),
  })

  useEffect(() => {
    try {
      const data = tryRestoreActivityFromStorage(setActivity)
      methods.reset({ activity: data })
    } catch {
      // Nothing to do
    }
  }, [setActivity])

  const onSubmit = (formValues: SimulatorActivity) => {
    if (formValues.activity !== undefined) {
      setActivity(formValues.activity)
      saveActivityToStorage(formValues.activity)
      navigate('/inscription/preparation/publics')
    }
  }

  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quelle est votre activité principale ?
        </h1>
      </div>
      <FormLayout>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <FormLayout.Row mdSpaceAfter>
            <Select
              options={[
                {
                  value: '',
                  label: 'Sélectionnez votre activité principale',
                },
                ...mainActivityOptions,
              ]}
              {...methods.register('activity')}
              error={methods.formState.errors.activity?.message}
              label="Activité principale"
              required
            />
          </FormLayout.Row>
          <div className={commonStyles['action-bar']}>
            <Button
              as="a"
              to="/inscription/preparation/accueil-public"
              variant={ButtonVariant.SECONDARY}
              label="Retour"
            />
            <BubbleStepper
              page={3}
              total={4}
              className={commonStyles['action-bar-stepper']}
            />
            <Button type="submit" label="Continuer" />
          </div>
        </form>
      </FormLayout>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorActivity
