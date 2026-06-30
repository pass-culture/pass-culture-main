import type { FieldValues, UseFormReturn } from 'react-hook-form'
import { useBlocker, useNavigate } from 'react-router'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeErrorIcon from '@/icons/stroke-error.svg'
import { Dialog } from '@/ui-kit/Dialog/Dialog'

import styles from './useFormNavigationGuard.module.scss'

/** @link https://app.notion.com/p/passcultureapp/Modale-de-pr-vention-de-changement-de-page-sur-les-formulaires-non-sauvegard-s-38bad4e0ff9880a89338f302f1361f38 */
export const useFormNavigationGuard = <
  TFieldValues extends FieldValues = FieldValues,
  // biome-ignore lint/suspicious/noExplicitAny: Follows original RHF shape.
  TContext = any,
  TTransformedValues extends TFieldValues = TFieldValues,
>({
  afterSubmitPath,
  form,
  isExternallyDirty = false,
  onSubmit,
}: {
  afterSubmitPath?: string | (() => string | undefined)
  form: UseFormReturn<TFieldValues, TContext, TTransformedValues>
  /** Used to pass an additional custom dirty state to the navigation guard, in addition to the RHF dirty state. */
  isExternallyDirty?: boolean
  /** @returns {Promise<boolean>} `true` if there is no error (thus allowing navigation), `false` otherwise. */
  onSubmit: (transformedFormValues: TTransformedValues) => Promise<boolean>
}): {
  navigationGuardedSubmitHandler: () => Promise<void>
  navigationGuardDialog: JSX.Element
} => {
  // https://react-hook-form.com/docs/useform/formstate#:~:text=isReady%5D)-,RULES
  // > Returned formState is wrapped with a Proxy to improve render performance
  // > and skip extra logic if specific state is not subscribed to.
  // > Therefore make sure you invoke or read it before a render in order to enable the state update.
  //
  // => `isDirty` and `isSubmitting` MUST be read here, during render, to keep them in sync with the form state.
  const { isDirty, isSubmitting } = form.formState

  const blocker = useBlocker(
    () => !isSubmitting && (isDirty || isExternallyDirty)
  )
  const navigate = useNavigate()

  const navigationGuardedSubmitHandler = form.handleSubmit(
    async (transformedFormValues: TTransformedValues) => {
      const canProceed = await onSubmit(transformedFormValues)
      if (!canProceed) {
        if (blocker.state === 'blocked') {
          blocker.reset()
        }

        return
      }

      const resolvedAfterSubmitPath =
        typeof afterSubmitPath === 'function'
          ? afterSubmitPath()
          : afterSubmitPath

      if (blocker.state === 'blocked') {
        blocker.proceed()
      } else if (resolvedAfterSubmitPath) {
        navigate(resolvedAfterSubmitPath)
      } else {
        form.reset(transformedFormValues)
      }
    },
    () => {
      // Close the guard dialog if there are the validation errors
      if (blocker.state === 'blocked') {
        blocker.reset()
      }
    }
  )

  const close = () => {
    if (blocker.state === 'blocked') {
      blocker.reset()
    }
  }

  const leaveWithoutSubmitting = () => {
    if (blocker.state === 'blocked') {
      blocker.proceed()
    }
  }

  const navigationGuardDialog = (
    <Dialog
      explanation="Vous avez des modifications non enregistrées. Voulez-vous les sauvegarder avant de quitter cette page ?"
      icon={strokeErrorIcon}
      onCancel={close}
      onClose={close}
      open={blocker.state !== 'unblocked'}
      title="Des modifications ont été apportées à cette page"
    >
      <div className={styles['confirm-dialog-actions']}>
        <Button
          isLoading={isSubmitting}
          label="Ignorer les modifications"
          onClick={leaveWithoutSubmitting}
          variant={ButtonVariant.SECONDARY}
        />
        <Button
          isLoading={isSubmitting}
          label="Enregistrer et quitter"
          onClick={navigationGuardedSubmitHandler}
        />
      </div>
    </Dialog>
  )

  return {
    navigationGuardedSubmitHandler,
    navigationGuardDialog,
  }
}
