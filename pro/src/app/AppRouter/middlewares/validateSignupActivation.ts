import { type LoaderFunctionArgs, redirect } from 'react-router'

import { api } from '@/apiClient/api'
import { getError, isErrorAPIError } from '@/apiClient/helpers'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { addSnackBar } from '@/commons/store/snackBar/reducer'
import { rootStore } from '@/commons/store/store'
import { initializeUser } from '@/commons/store/user/dispatchers/initializeUser'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { getUserDefaultPath } from '../utils/getUserDefaultPath'

const consumedTokenCalls = new Map<string, Promise<void>>()
export const __resetConsumedTokenCallsForTests = () => {
  consumedTokenCalls.clear()
}

const validateToken = (token: string): Promise<void> => {
  // Deduplication guard against React StrictMode double-mount (dev-only), which fires the route loader twice.
  // The backend `validate_passwordless_token` is single-use: it deletes the JTI from Redis on the first call,
  // so a second call with the same token => 404, which in turn toasts an error "Le lien est invalide".
  // The same guard also protects against any future router revalidation that would otherwise re-fire this loader.
  const consumedTokenCall = consumedTokenCalls.get(token)
  if (consumedTokenCall) {
    // = No need to process the token again, we already did it the first time
    return consumedTokenCall
  }

  const call = (async () => {
    try {
      await api.validateUser({ path: { token } })
      const user = await api.getProfile()
      await rootStore.dispatch(initializeUser({ user })).unwrap()

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
            description: errors.global ?? '',
            variant: SnackBarVariant.ERROR,
          })
        )
      } else {
        handleUnexpectedError(error, { isSilent: true })
      }
    }
  })()

  consumedTokenCalls.set(token, call)

  return call
}

export const validateSignupActivation = async (
  args: LoaderFunctionArgs<{ token: string }>
) => {
  const { token } = args.params
  if (!token) {
    throw redirect(getUserDefaultPath())
  }

  await validateToken(token)

  throw redirect(getUserDefaultPath())
}
