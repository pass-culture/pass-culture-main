import { FormikContextType, FormikProvider } from 'formik'

import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMailIcon from 'icons/full-mail.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'

type DefaultFormContactProps = {
  closeRequestFormDialog: () => void
  formik: FormikContextType<RequestFormValues>
  isPreview: boolean
}

export const DefaultFormContact = ({
  closeRequestFormDialog,
  formik,
  isPreview,
}: DefaultFormContactProps) => {
  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit} className={styles['form-container']}>
        <FormLayout>
          <FormLayout.Row>
            <TextInput label="Email" name="teacherEmail" disabled />
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
                minDate={new Date()}
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
              description="Décrivez le projet que vous souhaiteriez co-construire avec l’acteur culturel (Ex : Je souhaite organiser une visite que vous proposez dans votre théâtre pour un projet pédagogique autour du théâtre et de l’expression corporelle avec ma classe de 30 élèves entre janvier et mars. Je suis joignable par téléphone ou par mail.)"
            />
          </FormLayout.Row>
          <div className={styles['buttons-container']}>
            <Button
              onClick={closeRequestFormDialog}
              variant={ButtonVariant.SECONDARY}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              iconPosition={IconPositionEnum.LEFT}
              icon={fullMailIcon}
              disabled={isPreview}
            >
              Envoyer ma demande
            </Button>
          </div>
        </FormLayout>
      </form>
    </FormikProvider>
  )
}
