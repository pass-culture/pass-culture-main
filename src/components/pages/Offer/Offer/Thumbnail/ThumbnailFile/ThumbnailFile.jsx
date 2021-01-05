import React, { forwardRef } from 'react'

import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/thumbnail-sample.svg'

const ThumbnailFile = forwardRef(function ThumbnailFile(props, ref) {
  return (
    <form className="tnf-form">
      <ThumbnailSampleIcon />
      <p className="tnf-info">
        {'Utilisez de préférence un visuel en orientation portrait'}
      </p>
      <label className="tnf-file-label primary-link">
        {'Importer une image depuis l’ordinateur'}
        <input
          accept="image/png, image/jpeg"
          className="tnf-file-input"
          ref={ref}
          type="file"
        />
      </label>
      <p className="tnf-mandatory">
        {'Format supportés : JPG, PNG '}
        <br />
        {'Le poids du fichier de ne doit pas dépasser 10 Mo '}
        <br />
        {'La taille de l’image doit être supérieure à 400 x 400px '}
      </p>
    </form>
  )
})

export default ThumbnailFile
