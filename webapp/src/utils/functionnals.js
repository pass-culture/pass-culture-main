const each = (args, ...functions) => functions.filter(v => v).map(fn => fn(...args))

const compose = (...fns) =>
  fns
    .filter(v => v)
    .reverse()
    .reduce((prev, next) => value => next(prev(value)), value => value)

const pipe = (...fns) => compose.apply(compose, fns.reverse())

const noop = () => {}

const noopnoop = v => v

module.exports = { compose, each, noop, noopnoop, pipe }
