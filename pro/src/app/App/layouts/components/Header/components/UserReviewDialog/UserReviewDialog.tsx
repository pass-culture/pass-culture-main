import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import { api } from '@/apiClient/api'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullSmsIcon from '@/icons/full-sms.svg'
import strokeValidIcon from '@/icons/stroke-valid.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import {
  IconRadioGroup,
  type IconRadioGroupValues,
} from '@/ui-kit/form/IconRadioGroup/IconRadioGroup'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './UserReviewDialog.module.scss'
import { validationSchema } from './validationSchema'

export interface UserReviewDialogFormValues {
  userSatisfaction: string
  userComment: string
}

export const UserReviewDialog = ({
  dialogTrigger = (
    <Button
      variant={ButtonVariant.TERTIARY}
      color={ButtonColor.NEUTRAL}
      size={ButtonSize.SMALL}
      icon={fullSmsIcon}
      label="Donner mon avis"
    />
  ),
}: {
  dialogTrigger?: React.ReactNode
}) => {
  const snackBar = useSnackBar()
  const [displayConfirmation, setDisplayConfirmation] = useState<boolean>(false)
  const onSubmitReview = async (formValues: UserReviewDialogFormValues) => {
    try {
      if (!selectedOffererId) {
        return handleUnexpectedError(
          new FrontendError('`selectedOffererId` is null.'),
          { isSilent: true }
        )
      }

      await api.submitUserReview({
        offererId: selectedOffererId,
        location: location.pathname,
        pageTitle: document.title,
        userSatisfaction: formValues.userSatisfaction,
        userComment: formValues.userComment,
      })
      setDisplayConfirmation(true)
    } catch (e) {
      sendSentryCustomError(e)
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

  const initialValues: UserReviewDialogFormValues = {
    userSatisfaction: 'Correcte',
    userComment: '',
  }

  const form = useForm<UserReviewDialogFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
  })

  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const location = useLocation()

  const group: IconRadioGroupValues[] = [
    {
      label: 'Très mauvaise',
      icon: '😡',
      value: 'Très mauvaise',
    },
    {
      label: 'Mauvaise',
      icon: '🙁',
      value: 'Mauvaise',
    },
    {
      label: 'Correcte',
      icon: '😐',
      value: 'Correcte',
    },
    {
      label: 'Bonne',
      icon: '🙂',
      value: 'Bonne',
    },
    {
      label: 'Excellente',
      icon: '😍',
      value: 'Excellente',
    },
  ]

  const iconGroupError = form.formState.errors.userSatisfaction?.message
  const textareaError = form.formState.errors.userComment?.message

  return (
    <DialogBuilder
      onOpenChange={(open) => {
        if (!open) {
          setDisplayConfirmation(false)
          form.reset()
        }
      }}
      title={displayConfirmation ? undefined : 'Votre avis compte !'}
      trigger={dialogTrigger}
      variant={displayConfirmation ? 'default' : 'drawer'}
    >
      <div className={styles.dialog}>
        {!displayConfirmation ? (
          <FormProvider {...form}>
            <form
              className={styles['dialog-form']}
              onSubmit={form.handleSubmit((values) => onSubmitReview(values))}
            >
              <div className={styles['dialog-form-content']}>
                <ScrollToFirstHookFormErrorAfterSubmit />
                <IconRadioGroup
                  name="userSatisfaction"
                  error={iconGroupError}
                  legend="Comment évalueriez-vous votre expérience avec le pass Culture Pro ?"
                  group={group}
                  required
                  requiredIndicator="explicit"
                  value={form.watch('userSatisfaction')}
                  onChange={(e) => form.setValue('userSatisfaction', e)}
                />

                <TextArea
                  name="userComment"
                  value={form.watch('userComment')}
                  onChange={(e) => form.setValue('userComment', e.target.value)}
                  label={
                    <>
                      Pourriez-vous préciser ? Nous lisons tous les
                      commentaires.
                      <span aria-hidden="true"> 🙂</span>
                    </>
                  }
                  maxLength={500}
                  requiredIndicator="explicit"
                  required
                  error={textareaError}
                  className={styles['text-area-container']}
                />
              </div>

              <DialogBuilder.Footer>
                <div className={styles['dialog-buttons']}>
                  <Dialog.Close asChild>
                    <Button
                      variant={ButtonVariant.SECONDARY}
                      color={ButtonColor.NEUTRAL}
                      label="Annuler"
                    />
                  </Dialog.Close>
                  <Button type="submit" label="Envoyer" />
                </div>
              </DialogBuilder.Footer>
            </form>
          </FormProvider>
        ) : (
          <div className={styles['confirmation-dialog']}>
            <SvgIcon
              src={strokeValidIcon}
              alt=""
              className={styles['confirmation-dialog-icon']}
            />
            <div className={styles['confirmation-dialog-title']}>
              Merci beaucoup de votre participation !
            </div>
            <Dialog.Close asChild>
              <Button label="Fermer" />
            </Dialog.Close>
          </div>
        )}
      </div>
    </DialogBuilder>
  )
}
