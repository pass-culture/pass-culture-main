const SELECTOR_SEPARATOR = '::'

const mapArgsToSelectorCachedKeys = (...args) => args.join(SELECTOR_SEPARATOR)

export default mapArgsToSelectorCachedKeys
