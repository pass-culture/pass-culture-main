import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  TargetAudience,
} from '@/apiClient/v1'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

import { useSimulatorContext } from '../SimulatorContext'
import {
  type FormValues,
  validationSchema,
} from '../SimulatorEmail/validationSchema'
import {
  tryRestoreActivityFromStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from '../storage'

export const SimulatorEmail = (): JSX.Element => {
  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const {
    openToPublic,
    setOpenToPublic,
    activity,
    setActivity,
    siret,
    setSiret,
    targetAudiences,
    setTargetAudiences,
  } = useSimulatorContext()

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: { email: '' },
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const onSubmit = async (formValues: FormValues) => {
    try {
      const finalOpenToPublic =
        openToPublic ?? tryRestoreOpenToPublicFromStorage(setOpenToPublic)
      const finalActivity =
        (activity as ActivityOpenToPublic | ActivityNotOpenToPublic) ||
        tryRestoreActivityFromStorage(setActivity)
      const finalSiret = siret ?? tryRestoreSiretFromStorage(setSiret)
      const finalTargetAudience =
        targetAudiences?.individual !== undefined
          ? targetAudiences
          : tryRestoreTargetAudienceFromStorage(setTargetAudiences)

      const targets = []
      if (finalTargetAudience?.individual) {
        targets.push(TargetAudience.INDIVIDUAL)
      }
      if (finalTargetAudience?.collective) {
        targets.push(TargetAudience.COLLECTIVE)
      }

      if (
        !finalActivity ||
        !finalOpenToPublic ||
        !finalSiret ||
        targets.length === 0
      ) {
        throw new Error('Missing required values')
      }

      await api.sendSignupSimulationSummary({
        body: {
          isOpenToPublic: finalOpenToPublic === 'true',
          activity: finalActivity,
          siret: finalSiret.replaceAll(' ', ''),
          targets,
          email: formValues.email,
        },
      })
      navigate('/inscription/preparation/email-confirmation')
    } catch (error) {
      if (isErrorAPIError(error) && error.status < 500) {
        serializeApiErrors(error.body, setError)
      } else {
        sendSentryCustomError(error)
        snackBar.error('Une erreur est survenue')
      }
    }
  }

  return (
    <div className={commonStyles['content']}>
      <h1 className={commonStyles['title']}>
        Recevez votre liste de justificatifs par email
      </h1>
      <h2 className={commonStyles['subtitle']}>
        Retrouvez la liste de vos justificatifs et reprenez votre inscription à
        tout moment depuis votre boîte mail.
      </h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormLayout>
          <FormLayout.Row>
            <TextInput
              label="Adresse email"
              description="Format : email@exemple.com"
              error={errors.email?.message}
              required
              requiredIndicator="hidden"
              type="email"
              {...register('email')}
            />
          </FormLayout.Row>
          <div className={commonStyles['action-bar']}>
            <Button
              as="a"
              to="/inscription/preparation/resultats"
              variant={ButtonVariant.SECONDARY}
              label="Retour"
            />
            <Button
              type="submit"
              disabled={isSubmitting}
              label="Recevoir la liste"
            />
          </div>
        </FormLayout>
      </form>
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorEmail
