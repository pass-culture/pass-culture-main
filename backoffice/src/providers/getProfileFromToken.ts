import base64url from 'base64url';
import jwtDecode from 'jwt-decode';

export default (tokenJson: string) => {
    const token = JSON.parse(tokenJson);

    const jwt = jwtDecode(token.id_token)
    return jwt
}