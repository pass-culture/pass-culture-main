import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { FormProvider, useForm } from 'react-hook-form'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import { isDateValid } from 'commons/utils/date'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import fullMailIcon from 'icons/full-mail.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { createCollectiveRequestPayload } from './createCollectiveRequestPayload'
import { DefaultFormContact } from './DefaultFormContact'
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

  const methods = useForm<RequestFormValues>({
    defaultValues: {
      teacherEmail: userEmail ?? '',
      description: '',
      offerDate: '',
    },
    resolver: yupResolver(validationSchema()),
  })

  const onSubmit = async (values: RequestFormValues) => {
    try {
      const payload = createCollectiveRequestPayload(values)
      await apiAdage.createCollectiveRequest(offerId, payload)
      notify.success('Votre demande a bien été envoyée')
      closeModal()
    } catch {
      notify.error(
        'Impossible de créer la demande.\nVeuillez contacter le support pass culture'
      )
      closeModal()
    }
  }

  const closeRequestFormDialog = async () => {
    if (!isPreview) {
      const v = methods.getValues()
      await apiAdage.logRequestFormPopinDismiss({
        iframeFrom: location.pathname,
        collectiveOfferTemplateId: offerId,
        comment: v.description,
        phoneNumber: v.teacherPhone,
        requestedDate: isDateValid(v.offerDate)
          ? new Date(v.offerDate).toISOString()
          : undefined,
        totalStudents: v.nbStudents,
        totalTeachers: v.nbTeachers,
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

  // Helper to render a single contact method
  const renderContactInfo = (
    label: string,
    value?: string | null,
    isMail?: boolean
  ) => {
    if (!value) {
      return null
    }
    return (
      <div>
        <span className={styles['form-description']}>
          Il vous propose de le faire {label} :
        </span>
        {isMail ? (
          <a
            href={`mailto:${value}`}
            className={styles['form-description-text-contact']}
            target="_blank"
            rel="noreferrer"
          >
            {value}
          </a>
        ) : (
          <span className={styles['form-description-text-contact']}>
            {value}
          </span>
        )}
      </div>
    )
  }

  const renderMultiContact = () => (
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
        {contactUrl && contactForm !== 'form' && (
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
        {contactForm === 'form' &&
          (userRole === AdageFrontRoles.REDACTOR || isPreview) && (
            <li>
              en renseignant{' '}
              <span className={styles['form-description-text-value']}>
                le formulaire ci-dessous
              </span>
            </li>
          )}
      </ul>

      {contactForm === 'form' &&
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

  // Determine which description element to render
  const getDescriptionElement = () => {
    if (contactEmail && !contactPhone && !contactUrl && !contactForm) {
      return renderContactInfo('par mail', contactEmail, true)
    }
    if (!contactEmail && contactPhone && !contactUrl && !contactForm) {
      return renderContactInfo('par téléphone', contactPhone)
    }
    if (!contactEmail && !contactPhone && contactUrl && !contactForm) {
      return (
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
    }
    if (!contactEmail && !contactPhone && !contactUrl && contactForm) {
      if (userRole === AdageFrontRoles.REDACTOR || isPreview) {
        return (
          <>
            <span className={styles['form-description']}>
              Vous pouvez le contacter en renseignant les informations
              ci-dessous.
            </span>
            <MandatoryInfo className={styles['form-mandatory']} />
            {isPreview && (
              <Callout className={styles['contact-callout']}>
                Vous ne pouvez pas envoyer de demande de contact car ceci est un
                aperçu de test du formulaire que verront les enseignants une
                fois l’offre publiée.
              </Callout>
            )}
          </>
        )
      }
      return (
        <Callout className={styles['contact-readonly']}>
          Vous ne pouvez voir les informations de contact du partenaire car vous
          n’avez pas les droits ADAGE adaptés
        </Callout>
      )
    }

    // Default case - multiple contacts
    return renderMultiContact()
  }

  return (
    <DialogBuilder
      variant="drawer"
      title="Vous souhaitez contacter ce partenaire ?"
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
    >
      {getDescriptionElement()}

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <DefaultFormContact />

          <DialogBuilder.Footer>
            <div className={styles['buttons-container']}>
              <Dialog.Close asChild>
                <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
              </Dialog.Close>

              <Button
                type="submit"
                iconPosition={IconPositionEnum.LEFT}
                icon={fullMailIcon}
                disabled={isPreview}
              >
                Envoyer ma demande
              </Button>
            </div>
          </DialogBuilder.Footer>
        </form>
      </FormProvider>
    </DialogBuilder>
  )
}
