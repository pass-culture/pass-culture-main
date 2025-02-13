/* istanbul ignore file */

// Component only for display (sub-components already tested)

import classNames from 'classnames'
import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { OffererMemberStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Layout } from 'app/App/layout/Layout'
import { GET_MEMBERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { OffererLinkEvents } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { validationSchema } from 'pages/Collaborators/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { EmailSpellCheckInput } from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'

import styles from './Collaborators.module.scss'

const SUCCESS_MESSAGE = "L'invitation a bien été envoyée."
const ERROR_MESSAGE = 'Une erreur est survenue lors de l’envoi de l’invitation.'

export const Collaborators = (): JSX.Element | null => {
  const offererId = useSelector(selectCurrentOffererId)

  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const [isLoading, setIsLoading] = useState(false)
  const [displayAllMembers, setDisplayAllMembers] = useState(false)

  const [showInvitationForm, setShowInvitationForm] = useState(false)

  const { data } = useSWR(
    [GET_MEMBERS_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      !offererIdParam ? null : api.getOffererMembers(offererIdParam),
    { fallbackData: null }
  )
  const members = data?.members ?? []

  const onSubmit = async ({ email }: { email: string }) => {
    try {
      if (!offererId) {
        return
      }
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

  const MAX_COLLABORATORS = 10

  if (!offererId) {
    return null
  }

  return (
    <Layout mainHeading='Collaborateurs'>
      <section className={styles['section']}>
        <h2 className={styles['main-list-title']}>Liste des collaborateurs</h2>
        {members.length > 0 && (
          <div className={styles['members-container']}>
            <div className={styles['members-inner']}>
              <table className={styles['members-list']}>
                <thead>
                  <tr className={styles['members-list-tr']}>
                    <th scope="col" className={styles['members-list-th']}>
                      Email
                    </th>
                    <th scope="col" className={styles['members-list-th']}>
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {members.map(
                    ({ email, status }, index) =>
                      !(
                        !displayAllMembers && index > MAX_COLLABORATORS - 1
                      ) && (
                        <tr key={email} className={styles['members-list-tr']}>
                          <td
                            className={classNames(
                              styles['member-email'],
                              styles['members-list-td']
                            )}
                          >
                            {email}
                          </td>
                          <td
                            className={classNames(
                              styles['member-status'],
                              styles['members-list-td']
                            )}
                          >
                            {status === OffererMemberStatus.VALIDATED
                              ? 'Validé'
                              : 'En attente'}
                          </td>
                        </tr>
                      )
                  )}
                </tbody>
              </table>
            </div>
            {members.length > MAX_COLLABORATORS && (
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
              Vous pouvez inviter des collaborateurs à rejoindre votre espace.
              Une invitation leur sera envoyée par email. Vous serez notifié
              quand ils auront rejoint l’espace.
            </p>
            <FormikProvider value={formik}>
              <Form className={styles['invitation-form']}>
                <FormLayout>
                  <FormLayout.Row
                    className={styles['invitation-email-wrapper']}
                  >
                    <EmailSpellCheckInput
                      name="email"
                      description="Format : email@exemple.com"
                      label="Adresse email"
                      className={styles['invitation-email-field']}
                    />
                    <Button
                      type="submit"
                      isLoading={isLoading}
                      className={styles['add-member-button']}
                      data-error={formik.errors.email ? 'true' : 'false'}
                    >
                      Inviter
                    </Button>
                  </FormLayout.Row>
                </FormLayout>
              </Form>
            </FormikProvider>
          </>
        )}
      </section>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Collaborators
