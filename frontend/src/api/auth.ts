/// <reference types="vite/client" />
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  ClientId: import.meta.env.VITE_COGNITO_APP_CLIENT_ID || ''
};

export const userPool = new CognitoUserPool(poolData);

export function loginWithCognito(email: string, password: string): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!poolData.UserPoolId || !poolData.ClientId) {
      return reject(new Error("Cognito credentials missing from .env"));
    }

    const authenticationDetails = new AuthenticationDetails({
      Username: email,
      Password: password
    });

    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool
    });

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (result) => {
        const token = result.getIdToken().getJwtToken();
        const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        
        if (!isLocalhost) {
          localStorage.setItem('bb_token', token);
          localStorage.setItem('bb_user', email);
        } else {
          sessionStorage.setItem('bb_token', token);
          sessionStorage.setItem('bb_user', email);
        }
        resolve(token);
      },
      onFailure: (err) => {
        reject(err);
      },
      newPasswordRequired: (_userAttributes, _requiredAttributes) => {
        reject(new Error("New password required. Please reset password via AWS Console."));
      }
    });
  });
}

export function signUpWithCognito(email: string, password: string): Promise<any> {
  return new Promise((resolve, reject) => {
    if (!poolData.UserPoolId || !poolData.ClientId) {
      return reject(new Error("Cognito credentials missing from .env"));
    }
    userPool.signUp(email, password, [], null as any, (err, result) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(result);
    });
  });
}
