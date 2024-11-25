import { useState } from "react";
import { Link } from "react-router-dom";
import Swal from "sweetalert2";
import "./styles.scss";
import { useLogin } from "api/login";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const loginMutation = useLogin();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Call the login mutation with payload
    loginMutation.mutate(
      { email, password },
      {
        onSuccess: (data) => {
          const { user, token } = data || {};
          window.localStorage.setItem("URLshortenerUser", JSON.stringify(user));
          window.localStorage.setItem("JSON_WEB_TOKEN", token);
          Swal.fire({
            icon: "success",
            title: "Login Successful!",
            text: "You have successfully logged in",
            confirmButtonColor: "#221daf",
          }).then(() => {
            setIsSubmitting(false);
            window.location.replace("/overview");
          });
        },
        onError: () => {
          Swal.fire({
            icon: "error",
            title: "Login Failed!",
            text: "An error occurred, please try again",
            confirmButtonColor: "#221daf",
          });
          setIsSubmitting(false);
        },
      }
    );
  };

  return (
    <div className="login-page">
      <section>
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-5">
              <div className="login-card">
                <h3>Welcome back! 👋🏼</h3>
                <form onSubmit={handleLogin}>
                  <div className="form-group">
                    <label>Email address</label>
                    <input
                      type="email"
                      placeholder="you@mail.com"
                      onChange={(e) => setEmail(e.target.value)}
                      className="form-control"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input
                      type="password"
                      placeholder="password"
                      onChange={(e) => setPassword(e.target.value)}
                      className="form-control"
                      required
                    />
                  </div>
                  <button className="btn btn-main btn-block mb-3" type="submit">
                    {isSubmitting ? "Logging in..." : "Login"}
                  </button>
                  <p>
                    I don’t have an account?{" "}
                    <Link to="/register">Create account</Link>
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Login;
