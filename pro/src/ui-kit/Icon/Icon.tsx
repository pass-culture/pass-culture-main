import React, { ImgHTMLAttributes } from 'react'

import { ROOT_PATH } from 'utils/config'

interface IPropsIcon extends ImgHTMLAttributes<HTMLImageElement> {
  png?: string
  svg?: string
  alt?: string
}

const Icon = ({ png, svg, alt = '', ...imgProps }: IPropsIcon): JSX.Element => {
  const iconUrl = svg
    ? `${ROOT_PATH}/icons/${svg}.svg`
    : `${ROOT_PATH}/icons/${png}.png`
  return <img alt={alt} src={iconUrl} {...imgProps} />
}

export default Icon
