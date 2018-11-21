import minimist from 'minimist'

const args = minimist(process.argv.slice(2))
const environment = args.env

const youngUser =
  environment && environment === 'local'
    ? {
        email: 'pctest.jeune93.0@btmx.fr',
        password: 'pctest.Jeune93.0',
        publicName: 'Pc Test Jeune93 0',
      }
    : {
        email: 'pctest.jeune93.cafe0@btmx.fr',
        password: 'pctest.Jeune93.cafe0',
        publicName: 'Pc Test Jeune93 Cafe0',
      }

export default youngUser
