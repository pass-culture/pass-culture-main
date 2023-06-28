import { Form, useFormik, FormikProvider } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererMemberResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout/FormLayout'
import useNotification from 'hooks/useNotification'
import { ReactComponent as IcoPlusCircle } from 'icons/ico-plus-circle.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import EmailSpellCheckInput from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'

import styles from './AttachmentInvitations.module.scss'
import { validationSchema } from './validationSchema'

interface AttachmentInvitationsProps {
  offererId: number
}

const SECTION_ID = '#attachment-invitations-section'
const SUCCESS_MESSAGE = "L'invitation a bien été envoyée."
const ERROR_MESSAGE = "Une erreur est survenue lors de l'envoi de l'invitation."

const AttachmentInvitations = ({ offererId }: AttachmentInvitationsProps) => {
  const location = useLocation()
  const notify = useNotification()
  const [isLoading, setIsLoading] = useState(false)
  const [members, setMembers] = useState<
    Array<GetOffererMemberResponseModel> | undefined
  >()

  const onSubmit = async ({ email }: { email: string }) => {
    try {
      setIsLoading(true)
      await api.inviteMembers(offererId, { emails: [email] })
      notify.success(SUCCESS_MESSAGE)
    } catch {
      notify.error(ERROR_MESSAGE)
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
    fetchOffererMembers()
  })

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
      <div className={styles['main-list-title']}>
        <h2 className={styles['main-list-title-text']}>Collaborateurs</h2>
      </div>
      {!!members && (
        <>
          <h3 className={styles['subtitle']}>Membres de la structure</h3>
          <table className={styles['members-list']}>
            <thead>
              <tr>
                <th scope="col">Prénom & Nom</th>
                <th scope="col">Adresse email</th>
              </tr>
            </thead>
            <tbody>
              {members.map(({ firstName, lastName, email }) => (
                <tr>
                  <td>{`${firstName} ${lastName}`}</td>
                  <td>{email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h3 className={styles['subtitle']}>Ajout de collaborateurs</h3>
      <p className={styles['description']}>
        Vous pouvez inviter des collaborateurs à rejoindre votre espace.
      </p>
      <FormikProvider value={formik}>
        <Form>
          <FormLayout>
            <FormLayout.Row>
              <EmailSpellCheckInput
                name="email"
                placeholder="email@exemple.com"
                label="Adresse email"
                className={styles['invitation-email-field']}
              />
            </FormLayout.Row>

            <FormLayout.Row>
              <Button
                className={styles['add-member-button']}
                variant={ButtonVariant.TERNARY}
                Icon={IcoPlusCircle}
              >
                Ajouter un collaborateur
              </Button>
            </FormLayout.Row>

            <p className={styles['description']}>
              Votre invitation sera envoyée par mail à vos collaborateurs et
              vous serez notifié quand ils auront rejoint l’espace.
            </p>

            <FormLayout.Row>
              <SubmitButton
                // TODO: disable when all emails are empty
                isLoading={isLoading}
                variant={ButtonVariant.SECONDARY}
              >
                Envoyer une invitation
              </SubmitButton>
            </FormLayout.Row>
          </FormLayout>
        </Form>
      </FormikProvider>
    </section>
  )
}

export default AttachmentInvitations
