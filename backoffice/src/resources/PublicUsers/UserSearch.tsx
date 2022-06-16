import SearchIcon from '@mui/icons-material/Search'
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Grid,
  List,
  Typography,
} from '@mui/material'
import { ClassAttributes, HTMLAttributes, useState } from 'react'
import {
  Form,
  ReferenceField,
  SearchInput,
  ShowButton,
  useAuthenticated,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { eventMonitoring } from '../../libs/monitoring/sentry'
import { dataProvider } from '../../providers/dataProvider'
import { UserApiResponse } from '../Interfaces/UserSearchInterface'

import { BeneficiaryBadge } from './BeneficiaryBadge'
import { StatusBadge } from './StatusBadge'

const UpperCaseText = (
  props: JSX.IntrinsicAttributes &
    ClassAttributes<HTMLSpanElement> &
    HTMLAttributes<HTMLSpanElement>
) => (
  <span
    {...props}
    style={{
      textTransform: 'uppercase',
    }}
  ></span>
)

const UserCard = ({ record }: { record: UserApiResponse }) => {
  const {
    id,
    email,
    roles,
    isActive,
    firstName,
    lastName,
    phoneNumber,
  }: UserApiResponse = record
  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <div>
          <BeneficiaryBadge role={roles[0]} />
          <StatusBadge active={isActive} />
        </div>
        <Typography variant="subtitle1" component="h4" align="left">
          {firstName} <UpperCaseText>{lastName}</UpperCaseText>
        </Typography>
        <Typography variant="subtitle2" component="h5" align="left">
          <ReferenceField source="id" reference="/public_accounts/users/">
            <Typography>id user : {id}</Typography>
          </ReferenceField>
        </Typography>
        <Typography variant="body1" component="p" align="left">
          <strong>e-mail</strong>: {email}
        </Typography>
        <Typography variant="body1" component="p" align="left">
          <strong>tél : </strong> {phoneNumber}
        </Typography>
      </CardContent>
      <CardActions>
        <ShowButton
          onClick={event => event.preventDefault()}
          resource={'public_accounts/user'}
          label={'Consulter ce profil'}
        />

        <Button
          href={`/public_accounts/user/${id}`}
          variant={'text'}
          color={'secondary'}
        >
          Consulter ce profil
        </Button>
      </CardActions>
    </Card>
  )
}

function stopTypingOnSearch(event: {
  key: string
  stopPropagation: () => void
}) {
  if (event.key === 'Enter') {
    event.stopPropagation()
  }
}

export const UserSearch = () => {
  const [userData, setUserData] = useState([])
  useAuthenticated()

  async function formSubmit(params: FieldValues) {
    if (params && params.search) {
      setUserData([])
      try {
        const response = await dataProvider.searchList(
          'public_accounts/search',
          String(params.search)
        )
        console.log(response)
        if (response && response.data && response.data.length > 0) {
          setUserData(response.data)
        }
      } catch (error) {
        console.log(error)
        eventMonitoring.captureException(error)
      }
    }
  }

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
    >
      <Card
        style={{
          boxShadow: 'none',
          width: '100%',
          marginLeft: 0,
          paddingTop: '20px',
        }}
      >
        <CardContent>
          <Typography
            variant="h2"
            component="div"
            textAlign={userData.length === 0 ? 'center' : 'left'}
          >
            &nbsp;
          </Typography>

          <Typography
            variant={'subtitle1'}
            component={'p'}
            mb={2}
            gutterBottom
            textAlign={userData.length === 0 ? 'center' : 'left'}
          >
            Recherche un utilisateur à partir de son nom, mail ou numéro de
            téléphone
          </Typography>
          <Grid
            container
            justifyContent={userData.length === 0 ? 'center' : 'left'}
          >
            <Box>
              <Form onSubmit={formSubmit}>
                <div
                  style={{
                    justifyContent: 'center',
                    textAlign: 'center',
                  }}
                >
                  <SearchInput
                    helperText={false}
                    source={'q'}
                    name={'search'}
                    type={'text'}
                    fullWidth={userData.length === 0}
                    variant={'filled'}
                    style={{
                      marginLeft: 'auto',
                      marginRight: 5,
                    }}
                    onKeyUp={stopTypingOnSearch}
                  />

                  <Button
                    type={'submit'}
                    variant="contained"
                    size={'small'}
                    endIcon={<SearchIcon />}
                  >
                    Chercher
                  </Button>
                </div>
              </Form>
            </Box>
          </Grid>
          {userData.length > 0 && <div>{userData.length} résultat(s)</div>}
        </CardContent>
      </Card>
      <List>
        <Grid container spacing={2} sx={{ marginTop: '1em', minWidth: 275 }}>
          {userData.map(record => (
            <Grid
              key={record['id']}
              sx={{ minWidth: 275 }}
              xs={12}
              sm={6}
              md={4}
              lg={4}
              xl={4}
              item
            >
              <UserCard record={record} />
            </Grid>
          ))}
        </Grid>
      </List>
    </Grid>
  )
}
