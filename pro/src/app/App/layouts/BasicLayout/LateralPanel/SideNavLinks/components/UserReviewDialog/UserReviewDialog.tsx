import { yupResolver } from '@hookform/resolvers/yup'
import { useId, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import { api } from '@/apiClient/api'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import fullSmsIcon from '@/icons/full-sms.svg'
import strokeValidIcon from '@/icons/stroke-valid.svg'
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

interface UserReviewDialogProps {
  isAdminSpace?: boolean
}

export const UserReviewDialog = ({
  isAdminSpace = false,
}: Readonly<UserReviewDialogProps>) => {
  const location = useLocation()
  const snackBar = useSnackBar()
  const selectedOffererId = useAppSelector((state) =>
    isAdminSpace
      ? state.user.selectedAdminOfferer?.id
      : state.user.selectedPartnerVenue?.managingOfferer?.id
  )

  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [displayConfirmation, setDisplayConfirmation] = useState<boolean>(false)
  const formId = useId()

  const initialValues: UserReviewDialogFormValues = {
    userSatisfaction: 'Correcte',
    userComment: '',
  }
  const form = useForm<UserReviewDialogFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
  })

  const handleClose = () => {
    setIsOpen(false)
    setDisplayConfirmation(false)
    form.reset()
  }

  const onSubmitReview = async (formValues: UserReviewDialogFormValues) => {
    try {
      if (!selectedOffererId) {
        return handleUnexpectedError(
          new FrontendError('`selectedOffererId` is null.'),
          { isSilent: true }
        )
      }

      await api.submitUserReview({
        body: {
          offererId: selectedOffererId,
          location: location.pathname,
          pageTitle: document.title,
          userSatisfaction: formValues.userSatisfaction,
          userComment: formValues.userComment,
        },
      })
      setDisplayConfirmation(true)
    } catch (e) {
      sendSentryCustomError(e)
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

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
    <>
      <Button
        icon={fullSmsIcon}
        label="Donner mon avis"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        onClick={() => setIsOpen(true)}
      />
      <DetailedModal
        isOpen={isOpen}
        onClose={handleClose}
        title={displayConfirmation ? 'Merci !' : 'Votre avis compte !'}
        primaryAction={
          displayConfirmation ? (
            <Button label="Fermer" onClick={handleClose} />
          ) : (
            <Button type="submit" form={formId} label="Envoyer" />
          )
        }
        secondaryAction={
          !displayConfirmation ? (
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              onClick={handleClose}
              label="Annuler"
            />
          ) : undefined
        }
        isFooterFixed
      >
        {isOpen && (
          <div className={styles.dialog}>
            {!displayConfirmation && (
              <FormProvider {...form}>
                <form
                  id={formId}
                  className={styles['dialog-form']}
                  onSubmit={form.handleSubmit((values) =>
                    onSubmitReview(values)
                  )}
                >
                  <div>
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
                    <div className={styles['text-area-container']}>
                      <TextArea
                        name="userComment"
                        value={form.watch('userComment')}
                        onChange={(e) =>
                          form.setValue('userComment', e.target.value)
                        }
                        label={
                          <p>
                            Pourriez-vous préciser ? Nous lisons tous les
                            commentaires. <span aria-hidden="true">🙂</span>
                          </p>
                        }
                        maxLength={500}
                        initialRows={7}
                        requiredIndicator="explicit"
                        required
                        error={textareaError}
                      />
                    </div>
                  </div>
                </form>
              </FormProvider>
            )}

            {displayConfirmation && (
              <div className={styles['confirmation-dialog']}>
                <SvgIcon
                  src={strokeValidIcon}
                  alt=""
                  className={styles['confirmation-dialog-icon']}
                />
                <div className={styles['confirmation-dialog-title']}>
                  Merci beaucoup de votre participation !
                </div>
              </div>
            )}
          </div>
        )}
      </DetailedModal>
    </>
  )
}
