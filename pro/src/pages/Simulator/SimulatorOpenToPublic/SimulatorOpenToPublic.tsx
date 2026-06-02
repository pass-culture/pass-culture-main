import { yupResolver } from '@hookform/resolvers/yup'
import { BubbleStepper } from 'components/BubbleStepper/BubbleStepper'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OpenToPublicToggle } from 'components/OpenToPublicToggle/OpenToPublicToggle'
import { openToPublicValidationSchema } from 'components/OpenToPublicToggle/validationSchema'
import { Button } from 'design-system/Button/Button'
import { ButtonVariant } from 'design-system/Button/types'
import { useSimulatorContext } from 'pages/Simulator/SimulatorContext'
import styles from 'pages/Simulator/SimulatorTarget/SimulatorTarget.module.scss'
import {
  saveOpenToPublicToStorage,
  tryRestoreOpenToPublicFromStorage,
} from 'pages/Simulator/storage'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

type OpenToPublicFormValues = {
  isOpenToPublic: string | null
}

export const SimulatorOpenToPublic = (): JSX.Element => {
  const navigate = useNavigate()
  const { openToPublic, setOpenToPublic } = useSimulatorContext()

  const defaultValues: OpenToPublicFormValues = {
    isOpenToPublic: openToPublic ?? null,
  }

  const { clearErrors, watch, setValue, handleSubmit, reset, formState } =
    useForm({
      defaultValues,
      resolver: yupResolver<OpenToPublicFormValues, unknown, unknown>(
        openToPublicValidationSchema
      ),
    })

  useEffect(() => {
    try {
      const storedData = tryRestoreOpenToPublicFromStorage(setOpenToPublic)
      if (storedData) {
        reset({ isOpenToPublic: storedData })
      }
    } catch {
      // Nothing to do
    }
  }, [setOpenToPublic, reset])

  const onSubmit = (formValues: OpenToPublicFormValues) => {
    if (formValues.isOpenToPublic !== null) {
      saveOpenToPublicToStorage(formValues.isOpenToPublic)
      setOpenToPublic(formValues.isOpenToPublic)
      navigate('/inscription/preparation/activite')
    }
  }

  return (
    <div className={commonStyles['content']}>
      <h1 className={commonStyles['title']}>Accueil du public</h1>
      <h2 className={commonStyles['subtitle']}>
        Votre réponse adapte la suite de votre inscription, notamment les
        informations d'adresse demandées.
      </h2>
      <FormLayout>
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormLayout.Section>
            <FormLayout.Row className={styles['row-field-public']}>
              <OpenToPublicToggle
                error={formState.errors.isOpenToPublic?.message}
                onChange={(e) => {
                  clearErrors('isOpenToPublic')
                  setValue('isOpenToPublic', e.target.value)
                }}
                isOpenToPublic={watch('isOpenToPublic')}
                overrideDescription="Sélectionnez une des options."
              />
            </FormLayout.Row>

            <div className={commonStyles['action-bar']}>
              <Button
                as="a"
                to="/inscription/preparation/siret"
                variant={ButtonVariant.SECONDARY}
                label="Retour"
              />
              <BubbleStepper
                page={2}
                total={4}
                className={commonStyles['action-bar-stepper']}
              />
              <Button type="submit" label="Continuer" />
            </div>
          </FormLayout.Section>
        </form>
      </FormLayout>
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorOpenToPublic
