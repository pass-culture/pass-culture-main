import { type LoaderFunctionArgs, redirect } from 'react-router'

import { api } from '@/apiClient/api'
import { getError, isErrorAPIError } from '@/apiClient/helpers'
import { isFeatureActive } from '@/commons/store/features/selectors'
import { addSnackBar } from '@/commons/store/snackBar/reducer'
import { rootStore } from '@/commons/store/store'
import { initializeUser } from '@/commons/store/user/dispatchers/initializeUser'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

export const validateSignupActivation = async (
  args: LoaderFunctionArgs<{ token: string }>
) => {
  const state = rootStore.getState()
  if (!isFeatureActive(state, 'WIP_SWITCH_VENUE')) {
    return
  }

  const { token } = args.params
  if (!token) {
    throw redirect('/connexion')
  }

  try {
    await api.validateUser(token)
    const user = await api.getProfile()
    await rootStore.dispatch(initializeUser(user)).unwrap()

    rootStore.dispatch(
      addSnackBar({
        description:
          'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.',
        variant: SnackBarVariant.SUCCESS,
      })
    )
  } catch (error) {
    if (isErrorAPIError(error)) {
      const errors = getError(error)

      rootStore.dispatch(
        addSnackBar({
          description: errors.global,
          variant: SnackBarVariant.ERROR,
        })
      )
    }
  }

  throw redirect('/connexion')
}
