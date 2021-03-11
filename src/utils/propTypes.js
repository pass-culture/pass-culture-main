export const requiredIfComponentHasProp = (linkedPropName, requiredPropType) => (
  props,
  propName,
  componentName
) => {
  if (props[linkedPropName]) {
    if (!props[propName]) {
      return new Error(
        `The prop \`${propName}\` is marked as required in \`${componentName}\`, but its value is \`${props[propName]}\`.`
      )
    }
  }
  if (props[propName] && typeof props[propName] !== requiredPropType) {
    return new Error(
      `Invalid prop \`${propName}\` of type \`${typeof props[
        propName
      ]}\` supplied to \`${componentName}\`, expected \`${requiredPropType}\`.`
    )
  }
}
