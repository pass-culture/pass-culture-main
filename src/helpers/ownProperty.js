export const ownProperty = (obj, name) =>
  // lodash.get do not eval a 'null' value
  Object.prototype.hasOwnProperty.call(obj, name)

export default ownProperty
