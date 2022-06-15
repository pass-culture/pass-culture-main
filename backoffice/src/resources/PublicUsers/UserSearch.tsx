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
import {
  Form,
  ReferenceField,
  SearchInput,
  ShowButton,
  useAuthenticated,
} from 'react-admin'
import { dataProvider } from '../../providers/dataProvider'
import { ClassAttributes, HTMLAttributes, useState } from 'react'
import SearchIcon from '@mui/icons-material/Search'
import { UserApiInterface } from '../Interfaces/UserSearchInterface'
import { FieldValues } from 'react-hook-form'
import { StatusBadge } from './StatusBadge'
import { BeneficiaryBadge } from './BeneficiaryBadge'

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

const UserCard = (props: { record: any }) => {
  const record: UserApiInterface = props.record

  let statusBadge, activeBadge

  activeBadge = StatusBadge(record.isActive)
  statusBadge = BeneficiaryBadge(record.roles[0])
  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <div>
          {activeBadge} &nbsp;&nbsp;
          {statusBadge}
        </div>
        <br />
        <Typography variant="subtitle1" component="h4" align="left">
          {record.firstName} <UpperCaseText>{record.lastName}</UpperCaseText>
        </Typography>
        <Typography variant="subtitle2" component="h5" align="left">
          <ReferenceField source="id" reference="/public_accounts/users/">
            <Typography>id user : {record.id}</Typography>
          </ReferenceField>
        </Typography>
        <Typography variant="body1" component="p" align="left">
          <b>e-mail</b>: {record.email}
        </Typography>
        <Typography variant="body1" component="p" align="left">
          <b>tél : </b> {record.phoneNumber}
        </Typography>
      </CardContent>
      <CardActions>
        <ShowButton
          resource={'public_accounts/user'}
          label={'Consulter ce profil'}
        />

        <Button
          href={`/public_accounts/user/${record.id}`}
          variant={'text'}
          color={'secondary'}
        >
          Consulter ce profil
        </Button>
      </CardActions>
    </Card>
  )
}

export const UserSearch = () => {
  const [userData, setUserData] = useState([])
  useAuthenticated()
  const formSubmit = async (params: FieldValues) => {
    if (params && params.search) {
      setUserData([])
      try {
        const token = localStorage.getItem('token') || ''

        const response = await dataProvider.searchList(
          'public_accounts/search',
          String(params.search),
          {
            token: JSON.parse(token).id_token,
          }
        )
        if (response && response.data && response.data.length > 0) {
          setUserData(response.data)
        }
      } catch (error) {
        throw error
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
                    onKeyUp={event => {
                      if (event.key === 'Enter') {
                        event.stopPropagation()
                      }
                    }}
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
