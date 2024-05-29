import { Form, FormikProvider, useFormik } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  GetOffererMemberResponseModel,
  OffererMemberStatus,
} from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OffererLinkEvents } from 'core/FirebaseEvents/constants'
import { useNotification } from 'hooks/useNotification'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { EmailSpellCheckInput } from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'

import styles from './AttachmentInvitations.module.scss'
import { validationSchema } from './validationSchema'

interface AttachmentInvitationsProps {
  offererId: number
}

const SECTION_ID = '#attachment-invitations-section'
const SUCCESS_MESSAGE = "L'invitation a bien été envoyée."
const ERROR_MESSAGE = 'Une erreur est survenue lors de l’envoi de l’invitation.'

export const AttachmentInvitations = ({
  offererId,
}: AttachmentInvitationsProps) => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const notify = useNotification()
  const [isLoading, setIsLoading] = useState(false)
  const [displayAllMembers, setDisplayAllMembers] = useState(false)
  const [members, setMembers] = useState<Array<GetOffererMemberResponseModel>>(
    []
  )
  const [showInvitationForm, setShowInvitationForm] = useState(false)

  const onSubmit = async ({ email }: { email: string }) => {
    try {
      setIsLoading(true)
      await api.inviteMember(offererId, { email: email })
      members.unshift({
        email,
        status: OffererMemberStatus.PENDING,
      })
      formik.resetForm()
      logEvent(OffererLinkEvents.CLICKED_SEND_INVITATION, {
        offererId: offererId,
      })
      notify.success(SUCCESS_MESSAGE)
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400 && error.body.email) {
        formik.setFieldError('email', error.body.email)
      } else {
        notify.error(ERROR_MESSAGE)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const formik = useFormik({
    initialValues: { email: '' },
    onSubmit,
    validationSchema,
    validateOnChange: false,
  })

  useEffect(() => {
    const fetchOffererMembers = async () => {
      const { members } = await api.getOffererMembers(offererId)
      setMembers(members)
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    fetchOffererMembers()
  }, [])

  const shouldScrollToSection = location.hash === SECTION_ID
  const scrollToSection = useCallback((node: HTMLElement) => {
    if (shouldScrollToSection) {
      setTimeout(() => {
        node.scrollIntoView()
      }, 200)
    }
  }, [])

  return (
    <section className={styles['section']} ref={scrollToSection}>
      <h2 className={styles['main-list-title']}>Collaborateurs</h2>

      {members.length > 0 && (
        <div className={styles['members-container']}>
          <table className={styles['members-list']}>
            <thead>
              <tr>
                <th scope="col">Email</th>
                <th scope="col">Statut</th>
              </tr>
            </thead>
            <tbody>
              {members.map(
                ({ email, status }, index) =>
                  !(!displayAllMembers && index > 4) && (
                    <tr key={email}>
                      <td className={styles['member-email']}>{email}</td>
                      <td className={styles['member-status']}>
                        {status === OffererMemberStatus.VALIDATED
                          ? 'Validé'
                          : 'En attente'}
                      </td>
                    </tr>
                  )
              )}
            </tbody>
          </table>
          {members.length > 5 && (
            <Button
              onClick={() => setDisplayAllMembers(!displayAllMembers)}
              variant={ButtonVariant.TERNARY}
              icon={displayAllMembers ? fullUpIcon : fullDownIcon}
              className={styles['display-all-members-button']}
            >
              {displayAllMembers
                ? 'Voir moins de collaborateurs'
                : 'Voir plus de collaborateurs'}
            </Button>
          )}
        </div>
      )}

      {!showInvitationForm ? (
        <Button
          variant={ButtonVariant.SECONDARY}
          onClick={() => {
            logEvent(OffererLinkEvents.CLICKED_ADD_COLLABORATOR, {
              offererId: offererId,
            })
            setShowInvitationForm(true)
          }}
        >
          Ajouter un collaborateur
        </Button>
      ) : (
        <>
          <h3 className={styles['subtitle']}>Ajout de collaborateurs</h3>
          <p className={styles['description']}>
            Vous pouvez inviter des collaborateurs à rejoindre votre espace. Une
            invitation leur sera envoyée par email. Vous serez notifié quand ils
            auront rejoint l’espace.
          </p>
          <FormikProvider value={formik}>
            <Form className={styles['invitation-form']}>
              <FormLayout>
                <FormLayout.Row className={styles['invitation-email-wrapepr']}>
                  <EmailSpellCheckInput
                    name="email"
                    placeholder="email@exemple.com"
                    label="Adresse email"
                    className={styles['invitation-email-field']}
                  />
                  <div className={styles['add-member-button-wrapper']}>
                    <Button
                      type="submit"
                      isLoading={isLoading}
                      className={styles['add-member-button']}
                    >
                      Inviter
                    </Button>
                  </div>
                </FormLayout.Row>
              </FormLayout>
            </Form>
          </FormikProvider>
        </>
      )}
    </section>
  )
}
