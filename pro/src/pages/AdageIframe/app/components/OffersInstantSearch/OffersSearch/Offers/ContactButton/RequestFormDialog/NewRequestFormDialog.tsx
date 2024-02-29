import { useFormik } from 'formik'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Dialog from 'components/Dialog/Dialog'
import MandatoryInfo from 'components/FormLayout/FormLayoutMandatoryInfo'
import useNotification from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { isDateValid } from 'utils/date'

import { createCollectiveRequestAdapter } from './adapter/createCollectiveRequestAdapter'
import DefaultFormContact from './DefaultFormContact'
import styles from './NewRequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface NewRequestFormDialogProps {
  closeModal: () => void
  offerId: number
  userEmail?: string | null
  userRole: AdageFrontRoles
  contactEmail: string
  contactPhone: string
  contactForm: string
  contactUrl: string
}

const NewRequestFormDialog = ({
  closeModal,
  offerId,
  userEmail,
  userRole,
  contactEmail,
  contactPhone,
  contactForm,
  contactUrl,
}: NewRequestFormDialogProps): JSX.Element => {
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

  const getDescriptionElement = () => {
    if (contactEmail && !contactPhone && !contactUrl && !contactForm) {
      return renderContactElement('par mail', contactEmail)
    }
    if (!contactEmail && contactPhone && !contactUrl && !contactForm) {
      return renderContactElement('par téléphone', contactPhone)
    }
    if (!contactEmail && !contactPhone && contactUrl && !contactForm) {
      return renderCustomFormElement()
    }
    if (!contactEmail && !contactPhone && !contactUrl && contactForm) {
      return renderDefaultFormElement()
    }
    return renderMultiContactElement(
      {
        contactEmail,
        contactPhone,
      },
      contactForm === 'form',
      contactUrl.length > 0
    )
  }

  const renderContactElement = (
    description: string,
    value: string | null | undefined
  ) => (
    <div>
      <span className={styles['form-description']}>
        Il vous propose de le faire {description} :
      </span>
      <span className={styles['form-description-text-contact']}>{value}</span>
    </div>
  )

  const renderMultiContactElement = (
    {
      contactEmail,
      contactPhone,
    }: { contactEmail: string; contactPhone: string },
    isDefaultForm: boolean,
    isCustomForm: boolean
  ) => (
    <div className={styles['form-description']}>
      <span>Il vous propose de le faire :</span>
      <ul className={styles['form-description-list']}>
        {contactEmail && (
          <li>
            par mail :{' '}
            <span className={styles['form-description-text-value']}>
              {contactEmail}
            </span>
          </li>
        )}
        {contactPhone && (
          <li>
            par téléphone :{' '}
            <span className={styles['form-description-text-value']}>
              {contactPhone}
            </span>
          </li>
        )}
        {isCustomForm && (
          <li>
            <div className={styles['form-description-link']}>
              <i>via</i> son site :
              <ButtonLink
                variant={ButtonVariant.TERNARYPINK}
                className={styles['form-description-link-text']}
                link={{
                  to: contactUrl,
                  isExternal: true,
                  target: '_blank',
                }}
              >
                <SvgIcon
                  className={styles['form-icon']}
                  width="20"
                  alt="Nouvelle fenêtre"
                  src={fullLinkIcon}
                />
                Aller sur le site
              </ButtonLink>
            </div>
          </li>
        )}

        {isDefaultForm && (
          <li>
            en renseignant{' '}
            <span className={styles['form-description-text-value']}>
              le formulaire ci-dessous
            </span>
          </li>
        )}
      </ul>
      {isDefaultForm && (
        <>
          <hr />
          <MandatoryInfo className={styles['form-mandatory']} />
          <DefaultFormContact
            closeRequestFormDialog={closeRequestFormDialog}
            formik={formik}
          />
        </>
      )}
    </div>
  )

  const renderCustomFormElement = () => (
    <div>
      <div className={styles['form-description-link-site']}>
        Il vous propose de le faire <i>via</i> son site :
      </div>
      <ButtonLink
        variant={ButtonVariant.TERNARYPINK}
        className={styles['form-description-link-text']}
        link={{
          to: contactUrl,
          isExternal: true,
          target: '_blank',
        }}
      >
        <SvgIcon width="20" alt="Nouvelle fenêtre" src={fullLinkIcon} />
        Aller sur le site
      </ButtonLink>
    </div>
  )

  const renderDefaultFormElement = () => (
    <div>
      <span className={styles['form-description']}>
        Vous pouvez le contacter en renseignant les informations ci-dessous.
      </span>
      <MandatoryInfo className={styles['form-mandatory']} />
      <DefaultFormContact
        closeRequestFormDialog={closeRequestFormDialog}
        formik={formik}
      />
    </div>
  )

  return (
    <Dialog
      extraClassNames={styles['dialog-container']}
      onCancel={closeRequestFormDialog}
      title=""
      hideIcon
    >
      <span className={styles['form-title']}>
        Vous souhaitez contacter ce partenaire ?
      </span>
      {userRole === AdageFrontRoles.REDACTOR && <>{getDescriptionElement()}</>}
    </Dialog>
  )
}

export default NewRequestFormDialog
