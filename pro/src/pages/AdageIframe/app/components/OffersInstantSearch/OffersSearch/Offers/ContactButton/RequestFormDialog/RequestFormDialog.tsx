import { FormikProvider, useFormik } from 'formik'
import React from 'react'

import Dialog from 'components/Dialog/Dialog'
import FormLayout from 'components/FormLayout'
import useNotification from 'hooks/useNotification'
import { ReactComponent as MailIcon } from 'icons/ico-mail.svg'
import {
  Button,
  DatePicker,
  SubmitButton,
  TextArea,
  TextInput,
  TimePicker,
} from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface RequestFormDialogProps {
  closeModal: () => void
  contactEmail?: string
  contactPhone?: string | null
  venueName: string
  offererName: string
}

const RequestFormDialog = ({
  closeModal,
  contactEmail,
  contactPhone,
  venueName,
  offererName,
}: RequestFormDialogProps): JSX.Element => {
  const notify = useNotification()
  const initialValues = {
    teacherEmail: 'test@example.com',
    description: '',
  }
  const onSubmit = () => {
    // TODO : send request to backend
    closeModal()
    notify.success('Votre demande a bien été envoyée')
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
        Pour faciliter le traitement de votre demande par votre partenaire
        culturel nous vous invitons à remplir les informations ci-dessous
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
            <FormLayout.Row>
              <PhoneNumberInput
                label="Téléphone"
                name="teacherPhone"
                isOptional
              />
            </FormLayout.Row>
            <FormLayout.Row inline>
              <DatePicker
                label="Date souhaitée"
                minDateTime={new Date()}
                name="offerDate"
                isOptional
              />
              <TimePicker label="Heure" name="offerTime" isOptional />
            </FormLayout.Row>
            <FormLayout.Row inline>
              <TextInput
                label="Nombre d'élèves"
                name="nbStudents"
                type="number"
                isOptional
              />
              <TextInput
                label="Nombre d'accompagnateurs"
                name="nbTeachers"
                type="number"
                isOptional
              />
            </FormLayout.Row>
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
