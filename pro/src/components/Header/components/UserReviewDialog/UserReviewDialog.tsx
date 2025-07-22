import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { api } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { sendSentryCustomError } from 'commons/utils/sendSentryCustomError'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import fullSmsIcon from 'icons/full-sms.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import {
  IconRadioGroup,
  IconRadioGroupValues,
} from 'ui-kit/form/IconRadioGroup/IconRadioGroup'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './UserReviewDialog.module.scss'
import { validationSchema } from './validationSchema'

export interface UserReviewDialogFormValues {
  userSatisfaction: string
  userComment: string
}

export const UserReviewDialog = ({
  dialogTrigger = (
    <Button variant={ButtonVariant.QUATERNARY} icon={fullSmsIcon}>
      Donner mon avis
    </Button>
  ),
}: {
  dialogTrigger?: React.ReactNode
}) => {
  const notify = useNotification()
  const [displayConfirmation, setDisplayConfirmation] = useState<boolean>(false)
  const onSubmitReview = async (formValues: UserReviewDialogFormValues) => {
    try {
      await api.submitUserReview({
        offererId: selectedOffererId!,
        location: location.pathname,
        pageTitle: document.title,
        userSatisfaction: formValues.userSatisfaction,
        userComment: formValues.userComment,
      })
      setDisplayConfirmation(true)
    } catch (e) {
      sendSentryCustomError(e)
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
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

  const selectedOffererId = useSelector(selectCurrentOffererId)
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
                <MandatoryInfo
                  areAllFieldsMandatory
                  className={styles['dialog-mandatory']}
                />
                <ScrollToFirstHookFormErrorAfterSubmit />
                <IconRadioGroup
                  name="userSatisfaction"
                  error={iconGroupError}
                  legend="Comment évalueriez-vous votre expérience avec le pass Culture Pro ?"
                  group={group}
                  required
                  asterisk={false}
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
                  asterisk={false}
                  required
                  error={textareaError}
                  className={styles['text-area-container']}
                />
              </div>

              <DialogBuilder.Footer>
                <div className={styles['dialog-buttons']}>
                  <Dialog.Close asChild>
                    <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
                  </Dialog.Close>
                  <Button type="submit">Envoyer</Button>
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
              <Button>Fermer</Button>
            </Dialog.Close>
          </div>
        )}
      </div>
    </DialogBuilder>
  )
}
