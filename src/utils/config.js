const { NODE_ENV } = process.env

export const IS_DEV = NODE_ENV === 'development'

export const NEW = '_new_'

export const API_URL = IS_DEV ? 'http://localhost'
                              : 'https://pc-api.btmx.fr'

export const BROWSER_URL = IS_DEV ? 'http://localhost:3000'
                                  : 'https://pc.btmx.fr'

export const THUMBS_URL = IS_DEV
  ? `${API_URL}/static/object_store_data/thumbs`
  : `${API_URL}/static/object_store_data/thumbs`
