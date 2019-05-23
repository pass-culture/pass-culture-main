import get from 'lodash.get'
import { matchPath } from 'react-router-dom'

export const getMenuItemIdFromPathname = (pathto, prefix) => {
  const isvalidpatto = pathto && typeof pathto === 'string'
  const isvalidprefix = prefix && typeof prefix === 'string'
  if (!isvalidpatto || !isvalidprefix) {
    throw new Error('Missing arguments')
  }
  let basepath = pathto.split('/').slice(1, 2)
  basepath = (basepath && basepath.join('').toLowerCase()) || ''
  return `${prefix}-${basepath}-button`
}

export const getMenuItemPathTo = (location, item) => {
  const path = get(item, 'path')
  const currentPath = location.pathname
  const currentSearchQuery = location.search || ''
  const isactive = matchPath(currentPath, item)
  if (!isactive) return path
  const pathto = `${currentPath.replace('/menu', '')}${currentSearchQuery}`
  return pathto
}
