import { useFormik } from 'formik'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Dialog from 'components/Dialog/Dialog'
import MandatoryInfo from 'components/FormLayout/FormLayoutMandatoryInfo'
import useNotification from 'hooks/useNotification'
import { isDateValid } from 'utils/date'

import { createCollectiveRequestAdapter } from './adapter/createCollectiveRequestAdapter'
import DefaultFormContact from './DefaultFormContact'
import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface RequestFormDialogProps {
  closeModal: () => void
  contactEmail?: string | null
  contactPhone?: string | null
  offerId: number
  userEmail?: string | null
  userRole: AdageFrontRoles
}

const RequestFormDialog = ({
  closeModal,
  contactEmail,
  contactPhone,
  offerId,
  userEmail,
  userRole,
}: RequestFormDialogProps): JSX.Element => {
  const notify = useNotification()
  const initialValues = {
    teacherEmail: userEmail ?? '',
    description: '',
    offerDate: '',
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
  const closeRequestFormDialog = async () => {
    await apiAdage.logRequestFormPopinDismiss({
      iframeFrom: location.pathname,
      collectiveOfferTemplateId: offerId,
      comment: formik.values.description,
      phoneNumber: formik.values.teacherPhone,
      requestedDate: isDateValid(formik.values.offerDate)
        ? new Date(formik.values.offerDate).toISOString()
        : undefined,
      totalStudents: formik.values.nbStudents,
      totalTeachers: formik.values.nbTeachers,
    })
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
      onCancel={closeRequestFormDialog}
      title="Contacter le partenaire culturel"
      hideIcon
    >
      <div className={styles['contact-info-container']}>
        <a href={`mailto:${contactEmail}`}>{contactEmail}</a>
        {contactPhone}
      </div>
      {userRole === AdageFrontRoles.REDACTOR && (
        <>
          <div className={styles['form-description']}>
            <div className={styles['form-description-text']}>
              Si vous le souhaitez, vous pouvez contacter ce partenaire culturel
              en renseignant les informations ci-dessous.
            </div>
            <MandatoryInfo />
          </div>
          <DefaultFormContact
            closeRequestFormDialog={closeRequestFormDialog}
            formik={formik}
          />
        </>
      )}
    </Dialog>
  )
}

export default RequestFormDialog
