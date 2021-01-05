import React from 'react'

import { ReactComponent as ThumbnailSampleIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/thumbnail-sample.svg'

const ThumbnailFile = () => {
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
          type="file"
        />
      </label>
      <ul className="tnf-mandatory">
        <li>
          {'Formats supportés : JPG, PNG '}
        </li>
        <li>
          {'Le poids du fichier ne doit pas dépasser 10 Mo '}
        </li>
        <li>
          {'La taille de l’image doit être supérieure à 400 x 400px '}
        </li>
      </ul>
    </form>
  )
}

export default ThumbnailFile
