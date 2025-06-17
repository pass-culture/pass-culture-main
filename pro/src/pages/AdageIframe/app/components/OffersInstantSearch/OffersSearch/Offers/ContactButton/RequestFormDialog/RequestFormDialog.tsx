import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import { isDateValid } from 'commons/utils/date'
import { Dialog } from 'components/Dialog/Dialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import fullMailIcon from 'icons/full-mail.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { PhoneNumberInput } from 'ui-kit/formV2/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { createCollectiveRequestPayload } from './createCollectiveRequestPayload'
import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface RequestFormDialogProps {
  closeModal: () => void
  offerId: number
  userEmail?: string | null
  userRole?: AdageFrontRoles
  contactEmail: string
  contactPhone: string
  contactForm: string
  contactUrl: string
  isPreview: boolean
  isDialogOpen: boolean
  dialogTriggerRef?: React.RefObject<HTMLButtonElement>
}

export const RequestFormDialog = ({
  closeModal,
  offerId,
  userEmail,
  userRole,
  contactEmail,
  contactPhone,
  contactForm,
  contactUrl,
  isPreview,
  isDialogOpen,
  dialogTriggerRef,
}: RequestFormDialogProps): JSX.Element => {
  const notify = useNotification()

  const initialValues = {
    teacherEmail: userEmail ?? '',
    description: '',
    offerDate: new Date(),
    teacherPhone: '',
    nbStudents: 0,
    nbTeachers: 0,
  }

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RequestFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
  })

  const onSubmit = async (formValues: RequestFormValues) => {
    const payload = createCollectiveRequestPayload(formValues)
    try {
      await apiAdage.createCollectiveRequest(offerId, payload)
      notify.success('Votre demande a bien été envoyée')
      closeModal()
    } catch {
      notify.error(
        'Impossible de créer la demande.\nVeuillez contacter le support pass culture'
      )
      closeModal()
      return
    }
  }

  const closeRequestFormDialog = async () => {
    if (!isPreview) {
      const values = watch()
      await apiAdage.logRequestFormPopinDismiss({
        iframeFrom: location.pathname,
        collectiveOfferTemplateId: offerId,
        comment: values.description,
        phoneNumber: values.teacherPhone,
        requestedDate: isDateValid(values.offerDate)
          ? new Date(values.offerDate).toISOString()
          : undefined,
        totalStudents: values.nbStudents,
        totalTeachers: values.nbTeachers,
      })
    }
    closeModal()
  }

  const logContactUrl = () => {
    apiAdage.logContactUrlClick({
      iframeFrom: location.pathname,
      offerId,
    })
  }

  const getDescriptionElement = () => {
    if (contactEmail && !contactPhone && !contactUrl && !contactForm) {
      return renderContactElement('par mail', contactEmail, 'mail')
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
    value: string | null | undefined,
    type?: string
  ) => (
    <div>
      <span className={styles['form-description']}>
        Il vous propose de le faire {description} :
      </span>
      {type === 'mail' ? (
        <a
          href={`mailto:${value}`}
          className={styles['form-description-text-contact']}
          target="_blank"
          rel="noreferrer"
        >
          {value}
        </a>
      ) : (
        <span className={styles['form-description-text-contact']}>{value}</span>
      )}
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
            <a
              href={`mailto:${contactEmail}`}
              className={styles['form-description-text-value']}
              target="_blank"
              rel="noreferrer"
            >
              {contactEmail}
            </a>
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
              <i>via</i> son formulaire :
              <ButtonLink
                onClick={logContactUrl}
                variant={ButtonVariant.TERNARYBRAND}
                className={styles['form-description-link-text']}
                to={contactUrl}
                isExternal
                opensInNewTab
              >
                Aller sur le site
              </ButtonLink>
            </div>
          </li>
        )}

        {isDefaultForm &&
          (userRole === AdageFrontRoles.REDACTOR || isPreview) && (
            <li>
              en renseignant{' '}
              <span className={styles['form-description-text-value']}>
                le formulaire ci-dessous
              </span>
            </li>
          )}
      </ul>
      {isDefaultForm &&
        (userRole === AdageFrontRoles.REDACTOR || isPreview) && (
          <>
            <hr className={styles['separator']} />
            <MandatoryInfo className={styles['form-mandatory']} />
            {isPreview && (
              <Callout className={styles['contact-callout']}>
                Vous ne pouvez pas envoyer de demande de contact car ceci est un
                aperçu de test du formulaire que verront les enseignants une
                fois l’offre publiée.
              </Callout>
            )}
          </>
        )}
    </div>
  )

  const renderCustomFormElement = () => (
    <div>
      <div className={styles['form-description-link-site']}>
        Il vous propose de le faire <i>via</i> son formulaire :
      </div>
      <ButtonLink
        onClick={logContactUrl}
        variant={ButtonVariant.TERNARYBRAND}
        className={styles['form-description-link-text']}
        to={contactUrl}
        isExternal
        opensInNewTab
      >
        Aller sur le site
      </ButtonLink>
    </div>
  )

  const renderDefaultFormElement = () => (
    <div>
      {userRole === AdageFrontRoles.REDACTOR || isPreview ? (
        <>
          <span className={styles['form-description']}>
            Vous pouvez le contacter en renseignant les informations ci-dessous.
          </span>
          <MandatoryInfo className={styles['form-mandatory']} />
          {isPreview && (
            <Callout className={styles['contact-callout']}>
              Vous ne pouvez pas envoyer de demande de contact car ceci est un
              aperçu de test du formulaire que verront les enseignants une fois
              l’offre publiée.
            </Callout>
          )}
        </>
      ) : (
        <Callout className={styles['contact-readonly']}>
          Vous ne pouvez voir les informations de contact du partenaire car vous
          n’avez pas les droits ADAGE adaptés
        </Callout>
      )}
    </div>
  )

  return (
    <Dialog
      extraClassNames={styles['dialog-container']}
      onCancel={closeRequestFormDialog}
      title="Vous souhaitez contacter ce partenaire ?"
      hideIcon
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
    >
      {getDescriptionElement()}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className={styles['form-container']}
      >
        <FormLayout>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Email"
              {...register('teacherEmail')}
              disabled
              error={errors.teacherEmail?.message}
            />
          </FormLayout.Row>
          <div className={styles['form-row']}>
            <FormLayout.Row>
              <PhoneNumberInput
                label="Téléphone"
                {...register('teacherPhone')}
                error={errors.teacherPhone?.message}
              />
            </FormLayout.Row>
            <FormLayout.Row mdSpaceAfter>
              <DatePicker
                label="Date souhaitée"
                {...register('offerDate')}
                error={errors.offerDate?.message}
              />
            </FormLayout.Row>
            <FormLayout.Row mdSpaceAfter>
              <TextInput
                label="Nombre d'élèves"
                type="number"
                {...register('nbStudents', { valueAsNumber: true })}
                error={errors.nbStudents?.message}
              />
            </FormLayout.Row>
            <FormLayout.Row mdSpaceAfter>
              <TextInput
                label="Nombre d'accompagnateurs"
                type="number"
                isOptional
                {...register('nbTeachers', { valueAsNumber: true })}
                error={errors.nbTeachers?.message}
              />
            </FormLayout.Row>
          </div>
          <FormLayout.Row>
            <TextArea
              label="Que souhaitez vous organiser ?"
              maxLength={1000}
              {...register('description')}
              error={errors.description?.message}
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
    </Dialog>
  )
}
