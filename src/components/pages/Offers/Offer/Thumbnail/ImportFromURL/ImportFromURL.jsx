import * as PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import SubmitButton from 'components/layout/SubmitButton/SubmitButton'
import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offers/Offer/Thumbnail/assets/thumbnail-sample.svg'
import * as pcapi from 'repository/pcapi/pcapi'

const ImportFromURL = ({ isLoading, setIsLoading, setStep, setPreviewBase64, setURL, step }) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true)
  const [error, setError] = useState('')
  const [localUrl, setLocalUrl] = useState('')

  const checkUrl = useCallback(
    event => {
      const url = event.target.value

      setLocalUrl(url)
      setIsButtonDisabled(url === '')
      setURL(url)
      setError('')
    },
    [setURL]
  )

  const isURLFormatValid = url => /^(http|https)/.test(url)

  const isThereAnError = useCallback(
    async event => {
      event.preventDefault()

      setIsLoading(true)
      setIsButtonDisabled(true)

      if (!isURLFormatValid(localUrl)) {
        setError('Format d’URL non valide')
      } else {
        try {
          const result = await pcapi.validateDistantImage(localUrl)

          if (result.errors.length > 0) {
            setError(result.errors[0])
          } else {
            setPreviewBase64(result.image)
            setStep(step + 1)
            setIsButtonDisabled(false)
          }
        } catch {
          setError('Une erreur est survenue')
        }
      }

      setIsLoading(false)
    },
    [localUrl, setIsLoading, setPreviewBase64, setStep, step]
  )

  return (
    <form
      action="#"
      className="tnf-form"
    >
      <ThumbnailSampleIcon />
      <p className="tnf-info">
        Utilisez de préférence un visuel en orientation portrait
      </p>
      <TextInput
        disabled={isLoading}
        error={error}
        label="URL de l’image"
        name="url"
        onChange={checkUrl}
        placeholder="Ex : http://..."
        value={localUrl}
      />
      <SubmitButton
        className="primary-button tnf-url-button"
        disabled={isButtonDisabled}
        isLoading={isLoading}
        onClick={isThereAnError}
      >
        Valider
      </SubmitButton>
    </form>
  )
}

ImportFromURL.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  setIsLoading: PropTypes.func.isRequired,
  setPreviewBase64: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
  setURL: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default ImportFromURL
