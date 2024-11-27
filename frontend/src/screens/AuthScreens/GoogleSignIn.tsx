import React from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

const GoogleAuthButton = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = async (response:any) => {
    const { credential, clientId } = response; // Google token ID
    // Send token to the backend for verification and user session creation
    const res = await fetch('http://localhost:5000/social_login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: credential,
        clientId: clientId
      }),
    });

    if (res.ok) {
      const data = await res.json();
      const { user, token } = data || {};
      window.localStorage.setItem("URLshortenerUser", JSON.stringify(user));
      window.localStorage.setItem("JSON_WEB_TOKEN", token);

      // Redirect to the overview page
      window.location.replace("/overview");

    } else {
      console.error('Authentication failed');
    }
  };

  const handleLoginFailure = () => {
    console.error('Google login error');
  };

  return (
    <GoogleOAuthProvider clientId="736572233255-usvqanirqiarbk9ffhl6t6tl9br651fn.apps.googleusercontent.com">
      <GoogleLogin
        onSuccess={handleLoginSuccess}
        onError={handleLoginFailure}
      />
    </GoogleOAuthProvider>

  );
};

export default GoogleAuthButton;