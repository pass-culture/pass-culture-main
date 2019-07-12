export const formatPatch = (patch, config, creationFormKeys, modificationFormPermittedKeys) => {
  const { isCreatedEntity } = config || {}
  const formPatch = {}

  let patchKeys = modificationFormPermittedKeys
  if (isCreatedEntity) {
    patchKeys = creationFormKeys
  }

  patchKeys.forEach(key => {
    if (patch[key]) {
      formPatch[key] = patch[key]
    }
  })
  return formPatch
}
