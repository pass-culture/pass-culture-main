import { OBJECT_STORAGE_URL } from './config'

const getThumbUrl = thumbUrl => {
  if (!thumbUrl) return undefined
  const [base, suffix] = thumbUrl.split('/thumbs')
  return `${OBJECT_STORAGE_URL || base}/thumbs${suffix}`
}

export default getThumbUrl
