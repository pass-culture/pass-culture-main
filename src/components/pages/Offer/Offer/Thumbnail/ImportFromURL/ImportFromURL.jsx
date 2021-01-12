import React, { useCallback, useState } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/thumbnail-sample.svg'

const ImportFromURL = () => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true)
  const [url, setUrl] = useState('')

  const checkUrl = useCallback(event => {
    const url = event.target.value

    setIsButtonDisabled(url === '')
    setUrl(url)
  }, [])

  return (
    <form className="tnf-form">
      <ThumbnailSampleIcon />
      <p className="tnf-info">
        {'Utilisez de préférence un visuel en orientation portrait'}
      </p>
      <TextInput
        label="URL de l’image"
        name="url"
        onChange={checkUrl}
        placeholder="Ex : http://..."
        type="url"
        value={url}
      />
      <button
        className="primary-button tnf-url-button"
        disabled={isButtonDisabled}
        type="submit"
      >
        {'Valider'}
      </button>
    </form>
  )
}

export default ImportFromURL
