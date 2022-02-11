import React, { FunctionComponent } from 'react'

import style from './VenueImage.module.scss'

export type VenueImageProps = {
  url: string
  children?: never
}

export const VenueImage: FunctionComponent<VenueImageProps> = ({ url }) => (
  <img alt="Lieu" className={style['venue-image']} src={url} />
)
