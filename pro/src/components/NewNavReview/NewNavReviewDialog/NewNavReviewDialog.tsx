import * as Dialog from '@radix-ui/react-dialog'
import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { sendSentryCustomError } from 'commons/utils/sendSentryCustomError'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NewNavReviewDialog.module.scss'
import { validationSchema } from './validationSchema'

interface NewNavReviewDialogFormValues {
  isConvenient: string
  isPleasant: string
  comment: string
}

export const NewNavReviewDialog = () => {
  const notify = useNotification()
  const [displayConfirmation, setDisplayConfirmation] = useState<boolean>(false)
  const onSubmitReview = async (formValues: NewNavReviewDialogFormValues) => {
    try {
      await api.submitNewNavReview({
        offererId: selectedOffererId!,
        location: location.pathname,
        isPleasant: formValues.isPleasant === 'true' ? true : false,
        isConvenient: formValues.isConvenient === 'true' ? true : false,
        comment: formValues.comment,
      })
      setDisplayConfirmation(true)
    } catch (e) {
      sendSentryCustomError(e)
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

  const initialValues: NewNavReviewDialogFormValues = {
    isConvenient: '',
    isPleasant: '',
    comment: '',
  }

  const formik = useFormik<NewNavReviewDialogFormValues>({
    initialValues,
    onSubmit: onSubmitReview,
    validationSchema: validationSchema,
  })

  const selectedOffererId = useSelector(selectCurrentOffererId)
  const location = useLocation()

  return (
    <div className={styles.dialog}>
      {!displayConfirmation ? (
        <FormikProvider value={formik}>
          <Form>
            <Dialog.Title asChild>
              <h1 className={styles['dialog-title']}>Votre avis compte !</h1>
            </Dialog.Title>
            <fieldset>
              <legend className={styles['radio-legend']}>
                Selon vous, cette nouvelle interface est… ?
              </legend>
              <ol>
                <li className={styles['form-row']}>
                  <span className={styles['form-row-label']}>1.</span>
                  <div className={styles['radio-group']}>
                    <RadioButton
                      label={
                        <>
                          Moins pratique <span aria-hidden>🐢</span>
                        </>
                      }
                      name="isConvenient"
                      value="false"
                      className={styles['radio-button']}
                      withBorder
                    />
                    <RadioButton
                      label={
                        <>
                          Plus pratique <span aria-hidden>🐇</span>
                        </>
                      }
                      name="isConvenient"
                      value="true"
                      className={styles['radio-button']}
                      withBorder
                    />
                  </div>
                </li>
                <li className={styles['form-row']}>
                  <span className={styles['form-row-label']}>2.</span>
                  <div className={styles['radio-group']}>
                    <RadioButton
                      label={
                        <>
                          Moins agréable <span aria-hidden>🌧️</span>
                        </>
                      }
                      name="isPleasant"
                      value="false"
                      className={styles['radio-button']}
                      withBorder
                    />
                    <RadioButton
                      label={
                        <>
                          Plus agréable <span aria-hidden>🌈</span>
                        </>
                      }
                      name="isPleasant"
                      value="true"
                      className={styles['radio-button']}
                      withBorder
                    />
                  </div>
                </li>
              </ol>
            </fieldset>

            <TextArea
              name="comment"
              label={
                'Souhaitez-vous préciser ? Nous lisons tous les commentaires. 🙂'
              }
              maxLength={500}
              isOptional
            />

            <div className={styles['dialog-buttons']}>
              <Dialog.Close asChild>
                <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
              </Dialog.Close>
              <Button
                type="submit"
                disabled={
                  formik.values.isPleasant === initialValues.isPleasant ||
                  formik.values.isConvenient === initialValues.isConvenient
                }
              >
                Envoyer
              </Button>
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
