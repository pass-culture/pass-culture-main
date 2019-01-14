const trimValue = val => ((val && typeof val === 'string' && val) || '').trim()

export const slugify = (text = '', pprefix = '', psuffix = '') => {
  const a = 'àáäâèéëêìíïîòóöôùúüûñçßÿœæŕśńṕẃǵǹḿǘẍźḧ·/_,:;'
  const b = 'aaaaeeeeiiiioooouuuuncsyoarsnpwgnmuxzh------'
  const p = new RegExp(a.split('').join('|'), 'g')
  let prefix = trimValue(pprefix)
  prefix = (prefix && `${prefix}-`) || ''
  let suffix = trimValue(psuffix)
  suffix = (suffix && `-${suffix}`) || ''
  const result =
    text &&
    text !== '' &&
    text
      .toString()
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(p, c => b.charAt(a.indexOf(c)))
      .replace(/&/g, '-and-')
      .replace(/[^\w-]+/g, '')
      .replace(/--+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '')
  return (result && `${prefix}${result}${suffix}`) || ''
}

export default slugify
