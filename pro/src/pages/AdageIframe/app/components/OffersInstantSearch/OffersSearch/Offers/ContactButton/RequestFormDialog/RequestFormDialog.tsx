import { FormikProvider, useFormik } from 'formik'
import React from 'react'

import Dialog from 'components/Dialog/Dialog'
import FormLayout from 'components/FormLayout'
import MandatoryInfo from 'components/FormLayout/FormLayoutMandatoryInfo'
import useNotification from 'hooks/useNotification'
import { ReactComponent as MailIcon } from 'icons/ico-mail.svg'
import { Button, DatePicker, SubmitButton, TextArea, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { createCollectiveRequestAdapter } from './adapter/createCollectiveRequestAdapter'
import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface RequestFormDialogProps {
  closeModal: () => void
  contactEmail?: string
  contactPhone?: string | null
  venueName: string
  offererName: string
  offerId: number
  userEmail?: string | null
}

const RequestFormDialog = ({
  closeModal,
  contactEmail,
  contactPhone,
  venueName,
  offererName,
  offerId,
  userEmail,
}: RequestFormDialogProps): JSX.Element => {
  const notify = useNotification()
  const initialValues = {
    teacherEmail: userEmail ?? '',
    description: '',
  }
  const onSubmit = async (formValues: RequestFormValues) => {
    const response = await createCollectiveRequestAdapter({
      offerId,
      formValues,
    })
    if (!response.isOk) {
      notify.error(response.message)
      closeModal()
      return
    }
    notify.success('Votre demande a bien été envoyée')
    closeModal()
  }

  const formik = useFormik<RequestFormValues>({
    onSubmit: onSubmit,
    initialValues: initialValues,
    validationSchema: validationSchema,
  })
  return (
    <Dialog
      extraClassNames={styles['dialog-container']}
      onCancel={closeModal}
      title="Entrer en contact avec"
      hideIcon
    >
      <div className={styles.subtitle}>
        {venueName} - {offererName}
      </div>
      <div className={styles['contact-info-container']}>
        <a href={`mailto:${contactEmail}`}>{contactEmail}</a>
        {contactPhone}
      </div>
      <div className={styles['form-description']}>
        <div className={styles['form-description-text']}>
          Si vous le souhaitez, vous pouvez contacter ce partenaire culturel en
          renseignant les informations ci-dessous.
        </div>
        <MandatoryInfo />
      </div>

      <FormikProvider value={formik}>
        <form
          onSubmit={formik.handleSubmit}
          className={styles['form-container']}
        >
          <FormLayout>
            <FormLayout.Row>
              <TextInput label="E-Mail" name="teacherEmail" disabled />
            </FormLayout.Row>
            <div className={styles['form-row']}>
              <FormLayout.Row>
                <PhoneNumberInput
                  label="Téléphone"
                  name="teacherPhone"
                  isOptional
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <DatePicker
                  label="Date souhaitée"
                  minDateTime={new Date()}
                  name="offerDate"
                  isOptional
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="Nombre d'élèves"
                  name="nbStudents"
                  type="number"
                  isOptional
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="Nombre d'accompagnateurs"
                  name="nbTeachers"
                  type="number"
                  isOptional
                />
              </FormLayout.Row>
            </div>
            <FormLayout.Row>
              <TextArea
                countCharacters
                label="Que souhaitez vous organiser ?"
                maxLength={1000}
                name="description"
                placeholder="Décrivez votre demande (Ex: je souhaite organiser une visite dans votre théâtre avec ma classe de 30 élèves niveau seconde, entre le 1e janvier et le 31 mars. Je suis joignable par téléphone tous les jours de la semaine entre 12h et 14h...)"
              />
            </FormLayout.Row>
            <div className={styles['buttons-container']}>
              <Button onClick={closeModal} variant={ButtonVariant.SECONDARY}>
                Annuler
              </Button>
              <SubmitButton
                iconPosition={IconPositionEnum.LEFT}
                Icon={MailIcon}
              >
                Envoyer ma demande
              </SubmitButton>
            </div>
          </FormLayout>
        </form>
      </FormikProvider>
    </Dialog>
  )
}

export default RequestFormDialog
