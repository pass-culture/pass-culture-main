export const getMenuItemIdFromPathname = (pathto, prefix) => {
  const isvalidpatto = pathto && typeof pathto === 'string'
  const isvalidprefix = prefix && typeof prefix === 'string'
  if (!isvalidpatto || !isvalidprefix) {
    throw new Error('Missing arguments')
  }
  const basepath = pathto
    .split('/')
    .slice(1, 2)
    .join('')
    .toLowerCase()
  return `${prefix}-${basepath}-button`
}

export default getMenuItemIdFromPathname
