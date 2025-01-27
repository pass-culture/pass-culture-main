import * as Dialog from '@radix-ui/react-dialog'
import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { api } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { sendSentryCustomError } from 'commons/utils/sendSentryCustomError'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import {
  IconRadioGroup,
  IconRadioGroupValues,
} from 'ui-kit/form/IconRadioGroup/IconRadioGroup'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './UserReviewDialog.module.scss'
import { validationSchema } from './validationSchema'

interface UserReviewDialogFormValues {
  userSatisfaction: string
  userComment: string
}

export const UserReviewDialog = () => {
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

  const formik = useFormik<UserReviewDialogFormValues>({
    initialValues,
    onSubmit: onSubmitReview,
    validationSchema: validationSchema,
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

  return (
    <div className={styles.dialog}>
      {!displayConfirmation ? (
        <FormikProvider value={formik}>
          <Form>
            <Dialog.Title asChild>
              <h1 className={styles['dialog-title']}>Votre avis compte !</h1>
            </Dialog.Title>
            <MandatoryInfo
              areAllFieldsMandatory
              className={styles['dialog-mandatory']}
            />
            <ScrollToFirstErrorAfterSubmit />
            <IconRadioGroup
              name="userSatisfaction"
              legend="Comment évalueriez-vous votre expérience avec le pass Culture Pro ?"
              group={group}
              showMandatoryAsterisk={false}
            />

            <TextArea
              name="userComment"
              label={
                <>
                  Pourriez-vous préciser ? Nous lisons tous les commentaires.
                  <span aria-hidden="true"> 🙂</span>
                </>
              }
              maxLength={500}
              showMandatoryAsterisk={false}
              className={styles['text-area-container']}
            />

            <div className={styles['dialog-buttons']}>
              <Dialog.Close asChild>
                <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
              </Dialog.Close>
              <Button type="submit">Envoyer</Button>
            </div>
          </Form>
        </FormikProvider>
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
  )
}
