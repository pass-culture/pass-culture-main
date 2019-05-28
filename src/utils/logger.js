/* eslint no-console: 0 */
const usedebug = process.env.NODE_ENV === 'development'

const delegate = type => (...rest) => {
  if (!usedebug || !rest || rest.length < 1) return
  const [msg, val] = rest
  const args = [`[PC] ${msg}`, val].filter(v => v)
  console[type](...args)
}

const delegateFixme = () => (msg, val) => {
  // FIXME -> args length
  const css = 'background: #D19966; color: #FFFFFF'
  const args = [`%c${msg}`, css, val]
  delegate('log')(...args)
}

const logger = {
  // tricky console wrapper to get message stacks from
  // https://github.com/sixertoy/brackets-console-plus/blob/master/main.js#L417
  error: delegate('error'),
  fixme: delegateFixme(),
  log: delegate('log'),
  trace: delegateFixme(),
  warn: delegate('warn'),
}

export default logger
