import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { AdageFrontRoles } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { parseAndValidateFrenchPhoneNumber } from '@/commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useNotification } from '@/commons/hooks/useNotification'
import { isDateValid } from '@/commons/utils/date'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import { createCollectiveRequestPayload } from './createCollectiveRequestPayload'
import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'
import { validationSchema } from './validationSchema'

export interface RequestFormDialogProps {
  offerId: number
  userEmail?: string | null
  userRole?: AdageFrontRoles
  contactEmail: string
  contactPhone: string
  contactForm: string
  contactUrl: string
  isPreview: boolean
  onConfirmDialog: () => void
  dialogTriggerRef?: React.RefObject<HTMLButtonElement>
}

export const RequestFormDialog = ({
  offerId,
  userEmail,
  userRole,
  contactEmail,
  contactPhone,
  contactForm,
  contactUrl,
  isPreview,
  onConfirmDialog,
}: RequestFormDialogProps): JSX.Element => {
  const notify = useNotification()

  const initialValues = {
    teacherEmail: userEmail ?? '',
    description: '',
    offerDate: '',
    nbTeachers: 0,
    nbStudents: 0,
    teacherPhone: '',
  }

  const hookForm = useForm<RequestFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
  })

  const {
    watch,
    reset,
    formState: { isSubmitting },
  } = hookForm

  const onSubmit = async () => {
    const payload = createCollectiveRequestPayload(hookForm.getValues())
    try {
      await apiAdage.createCollectiveRequest(offerId, payload)
      notify.success('Votre demande a bien été envoyée')
      reset()
    } catch {
      notify.error(
        'Impossible de créer la demande.\nVeuillez contacter le support pass culture'
      )
      reset()
      return
    }
    onConfirmDialog()
  }

  const onCancel = async () => {
    if (!isPreview) {
      await apiAdage.logRequestFormPopinDismiss({
        iframeFrom: location.pathname,
        collectiveOfferTemplateId: offerId,
        comment: watch('description'),
        phoneNumber: watch('teacherPhone'),
        requestedDate: isDateValid(watch('offerDate'))
          ? watch('offerDate')
          : undefined,
        totalStudents: watch('nbStudents'),
        totalTeachers: watch('nbTeachers'),
      })
    }
    reset()
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
    <>
      <Dialog.DialogTitle>
        Vous souhaitez contacter ce partenaire ?
      </Dialog.DialogTitle>

      <form
        onSubmit={(e) => {
          e.stopPropagation()
          e.preventDefault()
          return hookForm.handleSubmit(onSubmit)(e)
        }}
      >
        {getDescriptionElement()}

        <FormLayout>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Email"
              {...hookForm.register('teacherEmail')}
              error={hookForm.formState.errors.teacherEmail?.message}
              required
              disabled
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <PhoneNumberInput
              {...hookForm.register('teacherPhone')}
              onBlur={(event) => {
                // This is because entries like "+33600110011invalid" are considered valid by libphonenumber-js,
                // We need to explicitely extract "+33600110011" that is in the .number property
                try {
                  const phoneNumber = parseAndValidateFrenchPhoneNumber(
                    event.target.value
                  ).number
                  hookForm.setValue('teacherPhone', phoneNumber)
                  // eslint-disable-next-line @typescript-eslint/no-unused-vars
                } catch (_e) {
                  // phone is considered invalid by the lib, so we does nothing here and let yup indicates the error
                }
              }}
              value={watch('teacherPhone')}
              onChange={(event) =>
                hookForm.setValue('teacherPhone', event.target.value)
              }
              error={hookForm.formState.errors.teacherPhone?.message}
              name="phoneNumber"
              label={'Téléphone'}
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <DatePicker
              className={styles['date-field-layout']}
              label="Date souhaitée"
              minDate={new Date()}
              error={hookForm.formState.errors.offerDate?.message}
              {...hookForm.register('offerDate')}
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Nombre d'élèves"
              {...hookForm.register('nbStudents')}
              error={hookForm.formState.errors.nbStudents?.message}
              type="number"
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Nombre d'accompagnateurs"
              {...hookForm.register('nbTeachers')}
              error={hookForm.formState.errors.nbTeachers?.message}
              type="number"
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <TextArea
              name="description"
              value={watch('description')}
              onChange={(e) => hookForm.setValue('description', e.target.value)}
              label="Que souhaitez vous organiser ?"
              maxLength={1000}
              description="Décrivez le projet que vous souhaiteriez co-construire avec l’acteur culturel (Ex : Je souhaite organiser une visite que vous proposez dans votre théâtre pour un projet pédagogique autour du théâtre et de l’expression corporelle avec ma classe de 30 élèves entre janvier et mars. Je suis joignable par téléphone ou par mail.)"
              required
              error={hookForm.formState.errors.description?.message}
            />
          </FormLayout.Row>
        </FormLayout>
        <DialogBuilder.Footer>
          <div className={styles['buttons-container']}>
            <Dialog.Close asChild>
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={onCancel}
                type="button"
              >
                Annuler
              </Button>
            </Dialog.Close>
            <Button
              type="submit"
              variant={ButtonVariant.PRIMARY}
              isLoading={isSubmitting}
              disabled={isPreview}
            >
              Envoyer ma demande
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </>
  )
}
