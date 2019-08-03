const getRemovedTranslationUrl = location => {
  const { pathname, search } = location
  return `${pathname.split('/translation')[0]}${search}`
}

export default getRemovedTranslationUrl
