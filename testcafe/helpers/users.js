import minimist from 'minimist'

const args = minimist(process.argv.slice(2))
const environment = args.env

const youngUser =
  environment && environment === 'local'
    ? {
        email: 'pctest.jeune.93@btmx.fr',
        password: 'azertyazertyP0$',
        publicName: 'Public Name',
      }
    : {
        email: 'pctest.cafe@btmx.fr',
        password: 'pctestcafe',
        publicName: 'Public Name',
      }

export default youngUser
