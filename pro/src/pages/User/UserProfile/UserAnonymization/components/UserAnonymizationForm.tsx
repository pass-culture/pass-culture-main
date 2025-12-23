import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { logout } from '@/commons/store/user/dispatchers/logout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './UserAnonymizationForm.module.scss'
import { getValidationSchema } from './validationSchema'

interface UserAnonymizationFormValues {
  email: string
}

export const UserAnonymizationForm = (): JSX.Element => {
  const dispatch = useAppDispatch()
  const snackBar = useSnackBar()
  const { currentUser } = useCurrentUser()

  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = useForm<UserAnonymizationFormValues>({
    defaultValues: { email: '' },
    resolver: yupResolver(getValidationSchema(currentUser.email)),
    mode: 'onBlur',
  })

  const onSubmit = async () => {
    try {
      await api.anonymize()
      dispatch(logout())
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className={styles['dialog-content']}>
        <div>
          <p className={styles['description']}>
            La suppression de votre compte entraînera :
          </p>
          <ul className={styles['list']}>
            <li>la fermeture de votre compte</li>
            <li>la suppression de vos données personnelles</li>
            <li>
              n‘entraînera pas la suppression de votre structure, vos
              collaborateurs y auront toujours accès
            </li>
          </ul>
        </div>
        <TextInput
          label="Confirmer votre adresse email"
          description="Format : email@exemple.com"
          required
          error={errors.email?.message}
          {...register('email')}
        />
        <Banner
          variant={BannerVariants.WARNING}
          title="Attention, cette action est irréversible."
        />
      </div>
      <div className={styles['dialog-footer']}>
        <Dialog.Close asChild>
          <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
        </Dialog.Close>
        <Button
          type="submit"
          variant={ButtonVariant.PRIMARY}
          isLoading={isSubmitting}
          testId="user-anonymization-submit"
        >
          Supprimer mon compte
        </Button>
      </div>
    </form>
  )
}
