import React, { useEffect } from 'react'
import PropTypes from 'prop-types'

import LoaderContainer from '../../../components/layout/Loader/LoaderContainer'
import { API_URL } from '../../../utils/config'
import { parse } from 'query-string'
import { toast } from 'react-toastify'

export const REQUEST_EMAIL_CHANGE_PAGE_LINK = '/profil/email'
export const SIGNIN_PAGE_LINK = '/connexion'
export const EMAIl_CHANGE_FAILED = "La modification de l'adresse email a échouée."
export const EMAIl_CHANGE_LINK_EXPIRED = 'Le lien a expiré, veuillez réessayer.'
export const EMAIL_CHANGE_SUCCESS = "L'adresse email a bien été modifiée."

const EmailChange = ({ location, history }) => {
  useEffect(() => {
    (async () => {
      const { token, expiration_timestamp } = parse(location.search)
      // We need to multiply by 1000 because UNIX timestamp is in seconds and js one is in milliseconds
      if (expiration_timestamp * 1000 < Date.now()) {
        toast.error(EMAIl_CHANGE_LINK_EXPIRED)
        history.push(REQUEST_EMAIL_CHANGE_PAGE_LINK)
        return
      }

      await fetch(`${API_URL}/beneficiaries/change_email`, {
        body: JSON.stringify({ token }),
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'PUT',
      })
        .then(response => {
          if (response.status !== 204) {
            toast.error(EMAIl_CHANGE_FAILED)
            history.push(REQUEST_EMAIL_CHANGE_PAGE_LINK)
            return
          }

          toast.success(EMAIL_CHANGE_SUCCESS)
          history.push(SIGNIN_PAGE_LINK)
        })
        .catch(() => {
          toast.error(EMAIl_CHANGE_FAILED)
          history.push(REQUEST_EMAIL_CHANGE_PAGE_LINK)
        })
    })()
  }, [history, location.search])

  return <LoaderContainer />
}

EmailChange.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    search: PropTypes.string.isRequired,
  }).isRequired,
}

export default EmailChange
